ME = $(shell pwd | sed -e 's/\//\\\//g')

install:
	cat ienabler.desktop | sed -e "s/Exec=/Exec=$(ME)\//g" -e 's/Icon=/Icon=$(ME)\//g' > $(HOME)/.local/share/applications/ienabler.desktop
