# Website release 2.2.1

Prepared October 5, 2026 from the app's maintained App Store listing and finished release screenshots. The App Store buttons let visitors download the app or check for the latest available update; this change does not submit or approve an App Store release.

- Home, About and Download cover Today, small steps and the sparrow, Talk, Personal Reflection, the offline KJV Bible, Elijah's painted seven-day retelling, devotion paths, Be Still, Listen Mode, Journal and Peace Garden with the illustrated Seed Shed.
- The release notes describe the clearer garden header/actions, grown-plant previews, roomier iPad layout, visible tablet beds and readability/accessibility updates.
- The eight finished iPhone panels are preserved as full-resolution PNGs with optimized WebP derivatives. See `screenshots-2.2.1.json` for provenance and checksums. Full panel captions remain visible without another phone frame. Historical ink art remains in the browser Still Waters preview.
- Legal Markdown and HTML are synchronized from the app. Disclosures cover device-only Walk/Journal data, guest operational retention and deletion, optional Apple sign-in, fresh-code deletion, RevenueCat reconciliation/restoration, and disabled-by-default Mercy Timeline. Subscription copy refers to the actual purchase offer rather than promising a trial on installation.

Validation: site build, AEO checks (37 articles and 305 redirect stubs), analytics checks (351 pages), JSON-LD parsing, local image paths, both identical legal Markdown files, and all 16 screenshot checksums pass. App `flutter analyze --fatal-infos` and `flutter test` pass (988 tests). No backend code changed.

Browser review used gstack's headless driver at 390 × 844 and 1440 × 1000. Home and Download load all eight panels without missing images or page overflow; About and both legal pages also have no mobile overflow. The mobile hero keeps the App Store action before the tall screenshot. Legal pages load successfully and show version 2.2.1. Still Waters navigation and its disabled-control fallback were verified; ink interaction could not be verified because this headless browser lacks WebGL 2 floating-point rendering. Its renderer was not changed.

This PR prepares the website update. Merging to main publishes it through the existing Pages configuration.
