# References and limitations

Sources consulted on 2026-11-11. These are mutable upstream URLs, not pinned source revisions or independently verified build artifacts. Third-party claims are not tests on this MAR-LX1A.

| Source | Relevance | Limitation |
| --- | --- | --- |
| [Android Platform-Tools](https://developer.android.com/tools/releases/platform-tools) | Official ADB/fastboot download | Does not supply a Huawei unlock method |
| [Android OEM USB drivers](https://developer.android.com/studio/run/oem-usb) | Windows driver setup | Initial fastboot failure's exact cause was not isolated |
| [Huawei HiSuite](https://consumer.huawei.com/en/support/hisuite/) | Official Windows connection and rollback tooling | Available rollback depends on actual device/server offer |
| [Huawei rollback guide](https://consumer.huawei.com/de/support/content/de-de00772016/) | Official EMUI 10-to-9 workflow and data-loss warning | General guide, not proof this current phone can reach EMUI 9.1 |
| [Huawei unlock-code service response](https://consumer.huawei.com/en/community/details/topicId-183915/) | Records official unlock-code service ending in 2018 | Does not determine exploit-based unlock feasibility |
| [PotatoNV compatibility and alternatives](https://github.com/kitsuned/PotatoNV) | Excludes Kirin 710 from PotatoNV; lists Kirin-Tool alternative and EMUI requirement | Not direct verification of Kirin-Tool on MAR-LX1A C431; tool website returned HTTP 403 |
| [Kirin 710 boot-ROM research](https://github.com/map220v/kirin710_bootrom_exploit) | Low-level loader research | Author reports testing on Honor 8X; not a validated P30 Lite procedure |
| [UBports porting introduction](https://docs.ubports.com/en/latest/porting/introduction/Intro.html) | Halium/vendor/rootfs architecture and Android bases | Generic guidance, not device support |
| [UBports kernel building](https://docs.ubports.com/en/latest/porting/build_and_boot/standalone_kernel_build.html) | Standalone workflow, config retrieval, minimum settings and deviceinfo | Exact patches/configuration depend on source and chosen port base |
| [UBports kernel installation](https://docs.ubports.com/en/latest/porting/build_and_boot/standalone_kernel_install.html) | Packaging workflow | Generic boot partition examples must be checked against Huawei layout |
| [UBports Lomiri bring-up](https://docs.ubports.com/en/latest/porting/configure_test_fix/Lomiri.html) | Device permissions/udev and GUI configuration | A booting kernel is not proof of a working UI |
| [Kirin710 kernel repository](https://github.com/Kirin710/android_kernel_huawei_kirin710) | Candidate source to inspect | Not selected, cloned, compiled or validated against this phone; fetching the connectivity directory failed |
| [P30 Lite SHRP recovery tree](https://github.com/Iceows/shrp_android_device_huawei_marie) | Device-specific recovery research lead | Recovery support is not an Ubuntu Touch port |
| [Archived Kirin 710 KernelSU tree](https://github.com/Coconutat/android_kernel_huawei_kirin710_KSU) | Earlier source/build research lead | Archived, modified for another purpose; not selected or verified for current kernel |
| [Kirin710 OSS UT/Halium tree](https://github.com/kirin710-oss/ubports_huawei_kirin710) | Potential reusable port configuration | Minimal README; branch name Halium-11 is not compatibility evidence for current vendor |
| [Original Kirin 710 Halium tree](https://github.com/Exynos7880-Linux/Huawei-kirin710) | Upstream of the above | No documented working P30 Lite configuration found in examined README |
| [Mate 20 Lite Droidian project](https://github.com/jglasovic/droidian-kirin710) | Author reports boot, display, Wi-Fi/SSH and documents Huawei connectivity initialization | Different phone/OS; headless-oriented default setup; no P30 Lite or accelerated Lomiri verification |

No image, firmware binary, third-party kernel source tree or unlock executable has been imported into this documentation repository.
