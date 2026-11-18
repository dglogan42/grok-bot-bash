# Reviewer targets. lint, test, and deb make no xAI API call.

.PHONY: lint test deb install clean

lint:
	shellcheck --shell=bash grok-bot

test:
	./grok-bot self-test

deb:
	set -eu; \
	version=$$(dpkg-parsechangelog -S Version); \
	test -n "$$version"; \
	stage="/tmp/grok-bot-bash-$$version"; \
	rm -rf "$$stage"; \
	cp -a "$$(pwd)" "$$stage"; \
	rm -rf "$$stage/.git"; \
	rm -f "$$stage"/grok-bot-bash_*.deb \
	      "$$stage"/grok-bot-bash_*.changes \
	      "$$stage"/grok-bot-bash_*.buildinfo \
	      "$$stage"/grok-bot-bash_*.dsc \
	      "$$stage"/grok-bot-bash_*.tar.xz \
	      "$$stage"/grok-bot-bash_*.tar.gz; \
	( cd "$$stage" && dpkg-buildpackage -us -uc --ignore-builtin-builddeps ); \
	cp -f "/tmp/grok-bot-bash_$${version}_all.deb" .; \
	rm -rf "$$stage"; \
	rm -f "/tmp/grok-bot-bash_$${version}.dsc" \
	      "/tmp/grok-bot-bash_$${version}.tar.xz" \
	      "/tmp/grok-bot-bash_$${version}.tar.gz" \
	      /tmp/grok-bot-bash_"$$version"_*.changes \
	      /tmp/grok-bot-bash_"$$version"_*.buildinfo \
	      "/tmp/grok-bot-bash_$${version}_all.deb"

install: deb
	set -eu; \
	version=$$(dpkg-parsechangelog -S Version); \
	dpkg -i "grok-bot-bash_$${version}_all.deb"

clean:
	set -eu; \
	version=$$(dpkg-parsechangelog -S Version); \
	rm -f "grok-bot-bash_$${version}_all.deb" \
	      "grok-bot-bash_$${version}.dsc" \
	      "grok-bot-bash_$${version}.tar.xz" \
	      "grok-bot-bash_$${version}.tar.gz" \
	      grok-bot-bash_"$$version"_*.changes \
	      grok-bot-bash_"$$version"_*.buildinfo
