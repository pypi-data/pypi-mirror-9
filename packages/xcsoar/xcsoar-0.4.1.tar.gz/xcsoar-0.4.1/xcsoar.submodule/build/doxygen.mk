DOXYGEN_OUTPUT_DIR = $(OUT)/doc

.PHONY: doco
doco: FORCE
	rm -rf $(DOXYGEN_OUTPUT_DIR)
	$(MKDIR) -p $(DOXYGEN_OUTPUT_DIR)
	cd $(DOC) && doxygen XCSoar.doxyfile
