# coding=UTF-8
# ex:ts=4:sw=4:et=on

# Copyright (c) 2013, Mathijs Dumon
# All rights reserved.
# Complete license can be found in the LICENSE file.

from traceback import print_exc
import logging
logger = logging.getLogger(__name__)

import time

from pyxrd.data import settings
from pyxrd.generic.models import ChildModel
from .refine_context import RefineContext, RefineSetupError

class Refiner(ChildModel):
    """
        A simple model that plugs onto the Mixture model. It provides
        the functionality related to refinement of parameters.
    """
    mixture = property(ChildModel.parent.fget, ChildModel.parent.fset)

    # ------------------------------------------------------------
    #      Methods & Functions
    # ------------------------------------------------------------
    def setup_context(self, store=False):
        """
            Creates a RefineContext object filled with parameters based on the
            current state of the Mixture object.
        """
        self.parent.setup_refine_options()
        self.context = RefineContext(
            parent=self.parent,
            options=self.parent.refine_options,
            store=store
        )

    def delete_context(self):
        """
            Removes the RefineContext
        """
        self.context = None

    def refine(self, stop, **kwargs):
        """
            This refines the selected properties using the selected algorithm.
            This should be run asynchronously to keep the GUI from blocking.
        """
        if self.context is None:
            raise RefineSetupError, "You need to setup the RefineContext before starting the refinement!"

        # Suppress updates:
        with self.mixture.needs_update.hold():
            with self.mixture.data_changed.hold():

                # If something has been selected: continue...
                if len(self.context.ref_props) > 0:
                    # Run until it ends or it raises an exception:
                    t1 = time.time()
                    try:
                        if stop is not None:
                            stop.clear()
                        logger.info("-"*80)
                        logger.info("Starting refinement with this setup:")
                        msg_frm = "%22s: %s"
                        refine_method = self.mixture.get_refinement_method()
                        logger.info(msg_frm % ("refinement method", refine_method))
                        logger.info(msg_frm % ("number of parameters", len(self.context.ref_props)))
                        logger.info(msg_frm % ("GUI mode", settings.GUI_MODE))
                        refine_method(self.context, stop=stop)
                    except any as error:
                        error.args += ("Handling run-time error: %s" % error,)
                        print_exc()
                        self.context.status = "error"
                        self.context.status_message = "Error occurred..."
                    else:
                        if stop is not None and stop.is_set():
                            self.context.status = "stopped"
                            self.context.status_message = "Stopping ..."
                        else:
                            self.context.status = "finished"
                            self.context.status_message = "Finished"
                    t2 = time.time()
                    logger.info('%s took %0.3f ms' % ("Total refinement", (t2 - t1) * 1000.0))
                    logger.info("-"*80)
                else: # nothing selected for refinement
                    self.context.status = "error"
                    self.context.status_message = "No parameters selected!"

            # Return the context to whatever called this
            return self.context

    pass # end of class
