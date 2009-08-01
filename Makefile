ME = $(shell pwd | sed -e 's/\//\\\//g')

install-local:
	@echo "Installing .desktop file in "$(HOME)"/.local/share/applications/ienabler.desktop"
	@cat ienabler.desktop | sed -e "s/Exec=/Exec=$(ME)\//g" -e 's/Icon=uclogo/Icon=$(ME)\/uclogo.svg/g' > $(HOME)/.local/share/applications/ienabler.desktop

uninstall-local:
	@echo "Removing .desktop file from "$(HOME)"/.local/share/applications/ienabler.desktop"
	@rm -f $(HOME)/.local/share/applications/ienabler.desktop

clean:
	@rm -f *.pyc
