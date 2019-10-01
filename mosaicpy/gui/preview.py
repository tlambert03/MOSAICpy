from PyQt5 import QtWidgets, QtCore
from mosaicpy.gui import img_dialog, helpers, SETTINGS
from mosaicpy import util, processplan
import os
import traceback
import sys
import numpy as np
import logging
from .helpers import get_main_window

logger = logging.getLogger(__name__)
_SPIMAGINE_IMPORTED = False


if not SETTINGS.value("disableSpimagineCheckBox", False, type=bool):
    try:
        # raise ImportError("skipping")
        with util.HiddenPrints():
            import spimagine

            _SPIMAGINE_IMPORTED = True
    except ImportError:
        logger.error("could not import spimagine!  falling back to matplotlib")


class PreviewPlan(processplan.PreviewPlan, QtCore.QObject):
    imp_starting = QtCore.pyqtSignal(object, dict)

    def __init__(self, *args, **kwargs):
        QtCore.QObject.__init__(self)
        super(PreviewPlan, self).__init__(*args, **kwargs)

    def _iterimps(self, data):
        for n, imp in enumerate(self.imps):
            if self.aborted:
                break
            self.imp_starting.emit(imp, self.meta)
            try:
                data, self.meta = imp(data, self.meta)
            except Exception as err:
                raise self.ProcessError(imp, n) from err
        return data, self.meta

    def abort(self):
        self.aborted = True


class PreviewWorker(QtCore.QObject):
    work_starting = QtCore.pyqtSignal(int)  # set progressbar maximum
    item_errored = QtCore.pyqtSignal(object)
    preview_update = QtCore.pyqtSignal(np.ndarray, dict)
    finished = QtCore.pyqtSignal()

    def __init__(self, plan, **kwargs):
        super(PreviewWorker, self).__init__()
        self.plan = plan

    def work(self):
        self.work_starting.emit(len(self.plan.t_range))
        try:
            for update in self.plan.execute():
                self.preview_update.emit(*update)
        except Exception as e:
            self.item_errored.emit(e)
        else:
            self.finished.emit()


if _SPIMAGINE_IMPORTED:

    class SpimagineWidget(spimagine.MainWidget):
        def __init__(self, arr=None, dx=1, dz=1, *args, **kwargs):
            super(SpimagineWidget, self).__init__(*args, **kwargs)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            if arr is not None:
                self.setModel(spimagine.DataModel(spimagine.NumpyData(arr)))
            self.transform.setStackUnits(dx, dx, dz)
            self.transform.setGamma(0.9)
            datamax = arr.max()
            datamin = arr.min()
            dataRange = datamax - datamin
            vmin_init = datamin - dataRange * 0.02
            vmax_init = datamax * 0.75
            self.transform.setMax(vmax_init)
            self.transform.setMin(vmin_init)
            self.transform.setZoom(1.3)

            # enable slice view by default
            self.sliceWidget.checkSlice.setCheckState(2)
            self.sliceWidget.glSliceWidget.interp = False
            self.checkSliceView.setChecked(True)
            self.sliceWidget.sliderSlice.setValue(int(arr.shape[-3] / 2))

            # self.impListView.add_image_processor(myImp())
            # self.impListView.add_image_processor(imageprocessor.LucyRichProcessor())
            self.setLoopBounce(False)
            self.settingsView.playInterval.setText("100")

            self.resize(1500, 900)
            self.show()
            self.raise_()

            # mainwidget doesn't know what order the colormaps are in
            colormaps = self.volSettingsView.colormaps
            self.volSettingsView.colorCombo.setCurrentIndex(colormaps.index("inferno"))
            self.sliceWidget.glSliceWidget.set_colormap("grays")

            # could have it rotating by default
            # win.rotate()


class HasPreview(object):
    abort_request = QtCore.pyqtSignal()

    def getSelectedPath(self):
        # if there is nothing in the list, just abort
        if self.listbox.rowCount() == 0:
            QtWidgets.QMessageBox.warning(
                self,
                "Nothing Added!",
                "Nothing to preview! Drop LLS experiment folders into the list",
                QtWidgets.QMessageBox.Ok,
                QtWidgets.QMessageBox.NoButton,
            )
            return

        # if there's only one item on the list auto-select it
        if self.listbox.rowCount() == 1:
            firstRowSelected = 0
        # otherwise, make sure the user has selected one
        else:
            selectedRows = self.listbox.selectionModel().selectedRows()
            if not len(selectedRows):
                QtWidgets.QMessageBox.warning(
                    self,
                    "Nothing Selected!",
                    "Please select an item (row) from the table to preview",
                    QtWidgets.QMessageBox.Ok,
                    QtWidgets.QMessageBox.NoButton,
                )
                return
            else:
                # if they select multiple, chose the first one
                firstRowSelected = selectedRows[0].row()

        return self.listbox.getPathByIndex(firstRowSelected)

    def onPreview(self):
        self.previewPath = self.getSelectedPath()
        if not self.previewPath:
            return

        # grab current list of imps and switch preview button to cancel
        self.currentImps = self.impListWidget.getImpList()
        self.previewButton.clicked.disconnect()
        self.previewButton.setText("CANCEL")
        self.previewButton.setEnabled(False)
        self.previewButton.clicked.connect(self.abortPreview)

        # get selectex C and T ranges
        procTRangetext = self.previewTRangeLineEdit.text()
        procCRangetext = self.previewCRangeLineEdit.text()
        if procTRangetext:
            tRange = helpers.string_to_iterable(procTRangetext)
        else:
            tRange = [0]
        if procCRangetext:
            cRange = helpers.string_to_iterable(procCRangetext)
        else:
            cRange = None  # means all channels

        # Create the dataDirectory object and ProcessPlan
        llsdir = self.listbox.getLLSObjectByPath(self.previewPath)
        # here is where we actually instantiate the ProcessPlan (PreviewPlan is a subclass)
        plan = PreviewPlan(llsdir, self.currentImps, t_range=tRange, c_range=cRange)

        # make sure the plan is going to work first...
        try:
            plan.plan()  # do sanity check here
        except plan.PlanError:
            self.on_item_finished()
            raise
        except plan.PlanWarning as e:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText(str(e) + "\n\nContinue anyway?")
            msg.setStandardButtons(
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
            )
            if msg.exec_() == QtWidgets.QMessageBox.Ok:
                plan.plan(skip_warnings=True)
            else:
                return
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            main_win = get_main_window()
            main_win.show_error_window(
                f"Unexpected {exc_type.__name__}:\n",
                title="Plan Load Error",
                info=str(exc_value),
                detail="".join(
                    traceback.format_exception(exc_type, exc_value, exc_traceback)
                ),
            )

            self.on_item_finished()
            return

        # make sure it hasn't disappeared
        if not os.path.exists(self.previewPath):
            self.statusBar.showMessage(
                "Skipping! path no longer exists: {}".format(self.previewPath), 5000
            )
            self.listbox.removePath(self.previewPath)
            self.previewButton.setEnabled(True)
            self.previewButton.setText("Preview")
            return

        # Create worker thread and connect signals
        worker, thread = helpers.newWorkerThread(PreviewWorker, plan)
        if self.prevBackendSpimagineRadio.isChecked() and _SPIMAGINE_IMPORTED:
            worker.finished.connect(self.showSpimagineWindow)
        else:
            worker.finished.connect(self.on_item_finished)
        worker.item_errored.connect(self.on_item_error)
        worker.preview_update.connect(self.update_preview)
        worker.plan.imp_starting.connect(self.emit_update)
        self.abort_request.connect(worker.plan.abort)

        # save stuff so it doesn't get garbage collected
        self.preview_threads = (thread, worker)
        self.preview_data = None
        thread.start()
        self.previewButton.setEnabled(True)

    @QtCore.pyqtSlot(object, dict)
    def emit_update(self, imp, meta):
        updatestring = "Rendering preview, t {} of {}: {}...".format(
            meta.get("t"), meta.get("nt"), imp.verb()
        )
        self.statusBar.showMessage(updatestring)

    def on_item_error(self, err=None):
        self.on_item_finished()
        raise err

    def append_preview_data(self, newdata):
        if self.preview_data is None:
            self.preview_data = newdata
        elif newdata.shape == self.preview_data.shape:
            self.preview_data = np.stack((self.preview_data, newdata))
        else:
            self.preview_data = np.concatenate(
                (self.preview_data, np.expand_dims(newdata, 0)), axis=0
            )

    @QtCore.pyqtSlot(np.ndarray, dict)
    def update_preview(self, array, meta):
        newwindow = self.preview_data is None
        if self.previewAborted:
            return
        self.append_preview_data(array)
        if self.prevBackendSpimagineRadio.isChecked() and _SPIMAGINE_IMPORTED:
            self._meta = meta
        else:
            # if there is already an open window and this is not the first timepoint
            # just append to the open window
            if len(self.spimwins) and not newwindow:
                self.spimwins[-1].update_data(self.preview_data)
            else:
                win = img_dialog.ImgDialog(
                    self.preview_data,
                    info=meta,
                    title=helpers.shortname(self.previewPath),
                )
                win.close_requested.connect(
                    lambda: self.spimwins.pop(self.spimwins.index(win))
                )
                self.spimwins.append(win)

    def abortPreview(self):
        self.previewAborted = True
        logger.info("Aborting preview ...")
        if self.preview_threads:
            self.preview_aborted = True
            self.abort_request.emit()
            self.previewButton.clicked.disconnect()
            self.previewButton.setText("ABORTING...")
            self.previewButton.setDisabled(True)

    def showSpimagineWindow(self):
        if self.preview_data is not None:
            metaparams = getattr(self, "_meta", {}).get("params", {})
            if np.squeeze(self.preview_data).ndim > 4:
                arrays = [
                    self.preview_data[:, i] for i in range(self.preview_data.shape[1])
                ]
            else:
                arrays = [np.squeeze(self.preview_data)]

            for arr in arrays:
                win = SpimagineWidget(
                    arr, dx=metaparams.get("dx", 1), dz=metaparams.get("dz", 1)
                )
                win.setWindowTitle(helpers.shortname(self.previewPath))
                self.spimwins.append(win)
        self.on_item_finished()

    def cleanup_preview_workers(self):
        if self.preview_threads:
            thread, worker = self.preview_threads
            worker.deleteLater()
            thread.quit()
            thread.wait()
            self.preview_threads = None

    def on_item_finished(self):
        self.cleanup_preview_workers()
        self.preview_data = None
        try:
            self.previewButton.clicked.disconnect()
        except Exception:
            pass
        self.previewButton.clicked.connect(self.onPreview)
        self.previewButton.setText("Preview")
        self.previewButton.setEnabled(True)
        self.previewAborted = False
        self.statusBar.showMessage("Ready")
