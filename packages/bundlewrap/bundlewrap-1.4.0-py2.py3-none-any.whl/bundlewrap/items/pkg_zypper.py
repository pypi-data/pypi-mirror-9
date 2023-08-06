# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from pipes import quote

from bundlewrap.exceptions import BundleError
from bundlewrap.items import Item, ItemStatus
from bundlewrap.utils import LOG
from bundlewrap.utils.text import bold, green, red
from bundlewrap.utils.text import mark_for_translation as _


ZYPPER_OPTS = "--non-interactive " + \
              "--non-interactive-include-reboot-patches " + \
              "--quiet"


def pkg_install(node, pkgname):
    return node.run("zypper {} install {}".format(ZYPPER_OPTS, quote(pkgname)))


def pkg_installed(node, pkgname):
    result = node.run(
        "zypper search --match-exact --installed-only "
                      "--type package {}".format(quote(pkgname)),
        may_fail=True,
    )
    if result.return_code != 0:
        return False
    else:
        return True


def pkg_remove(node, pkgname):
    return node.run("zypper {} remove {}".format(ZYPPER_OPTS, quote(pkgname)))


class ZypperPkg(Item):
    """
    A package installed by yum.
    """
    BLOCK_CONCURRENT = ["pkg_zypper"]
    BUNDLE_ATTRIBUTE_NAME = "pkg_zypper"
    ITEM_ATTRIBUTES = {
        'installed': True,
    }
    ITEM_TYPE_NAME = "pkg_zypper"

    def __repr__(self):
        return "<ZypperPkg name:{} installed:{}>".format(
            self.name,
            self.attributes['installed'],
        )

    def ask(self, status):
        before = _("installed") if status.info['installed'] \
            else _("not installed")
        after = green(_("installed")) if self.attributes['installed'] \
            else red(_("not installed"))
        return "{} {} → {}\n".format(
            bold(_("status")),
            before,
            after,
        )

    def fix(self, status):
        if self.attributes['installed'] is False:
            LOG.info(_("{node}:{bundle}:{item}: removing...").format(
                bundle=self.bundle.name,
                item=self.id,
                node=self.node.name,
            ))
            pkg_remove(self.node, self.name)
        else:
            LOG.info(_("{node}:{bundle}:{item}: installing...").format(
                bundle=self.bundle.name,
                item=self.id,
                node=self.node.name,
            ))
            pkg_install(self.node, self.name)

    def get_status(self):
        install_status = pkg_installed(self.node, self.name)
        item_status = (install_status == self.attributes['installed'])
        return ItemStatus(
            correct=item_status,
            info={'installed': install_status},
        )

    @classmethod
    def validate_attributes(cls, bundle, item_id, attributes):
        if not isinstance(attributes.get('installed', True), bool):
            raise BundleError(_(
                "expected boolean for 'installed' on {item} in bundle '{bundle}'"
            ).format(
                bundle=bundle.name,
                item=item_id,
            ))
