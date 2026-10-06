# Privacy Policy

**Last Updated: October 5, 2026 — App version 2.2.1**

## 1. Introduction

Jesus Says ("we," "our," or "App") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our mobile application. You may use the App's core features without manually creating an account or signing in with Apple. To operate the Service securely and apply abuse protections, purchase restoration, and usage limits, the App creates an anonymous Firebase Authentication account when you begin using the Service. That anonymous account is identified by a Firebase-generated UID rather than directly identifying information such as your real name or personal email address.

## 2. Information We Collect

### 2.1 Information You Provide

- **Talk to Jesus Conversation Data**: The App requests microphone access to record your spoken reflections. Your voice input is transcribed on-device or via Apple's Speech Recognition service, depending on your device and language settings, before being sent to our servers as text for spiritual guidance generation
- **Personal Reflection (Confession) Transcripts**: Audio reflections you record in the Personal Reflection feature may be processed on-device or via Apple's Speech Recognition service, depending on your device and language settings, before being sent to our servers as text for spiritual guidance generation. Your completed reflection entries (response cards and metadata) are stored locally in a unified journal store (iOS Keychain, key `journal_entries_device_v2`) with iCloud Keychain sync disabled (see §6 and §12.1)
- **Devotion Journey Transcripts**: Daily audio check-ins you record in the Devotion Journey feature may be processed on-device or via Apple's Speech Recognition service, depending on your device and language settings, before being sent to our servers as text for personalized devotional responses. Your completed devotion entries are also stored locally in the unified journal store (iOS Keychain, key `journal_entries_device_v2`) with iCloud Keychain sync disabled (see §6 and §12.1)
- **Listen Mode Playback**: Listen Mode uses local text-to-speech on your device. The spoken playback itself is not transmitted to our servers
- **Chapel Appearance**: Chapel lets you choose a bundled painted or moving view for Today and a day or evening light. The selected view and light are saved in local device preferences; both are cleared on sign-out or account/session deletion. Chapel does not upload your selection or download videos from our servers. A still image is shown when reduced motion is enabled or the device is not on Wi-Fi or Ethernet
- **Verse Library**: Saved verses are stored in iOS Keychain with `synchronizable: true`, so they may sync across your Apple devices through your own iCloud Keychain settings
- **Anonymous Firebase Account Information**: When you begin using the App, Firebase Authentication creates an anonymous account identified by a unique UID. We use this anonymous UID to operate the Service, enforce security protections, track purchase entitlements, restore eligible purchases, and support delete-account requests. By itself, this anonymous UID does not directly identify you by name or personal email address
- **Authentication Information**: If you choose to sign in with Apple, your account may also be linked to Apple-provided authentication tokens and any profile data you choose to share. Core features and paid entitlement do not require manual Apple sign-in
- **Device Information**: Device ID, app version, and platform information

- **Walk With, Small Steps and Peace Garden**: Your sparrow name, small-step progress, earned seeds, garden plants, story choices and saved story replies are stored in encrypted, device-only Keychain storage. When you send a typed or transcribed story reply, your words are sent through our backend to Google Gemini to prepare a response. We do not retain these story words as history on our backend. Operational allowance counters and request identifiers are retained for service security. Walk data is cleared on sign-out or session/account deletion.

### 2.2 Automatically Collected Information

- **Usage Data**: How you interact with the App
- **Device Information**: Device type, operating system, unique device identifiers
- **Log Data**: App performance and error logs

## 3. How We Use Your Information

We use the information we collect to:
- **Provide Generated Responses**: Your conversations are sent to Google Gemini to generate Bible reference suggestions and response text
- **In-App Bible Reading**: When you tap a verse reference, the App displays the full passage from the bundled English KJV Bible text included in the App; no additional personal data is sent for this feature
- **Improve the App**: Analyze usage patterns to enhance user experience
- **Authentication and Abuse Prevention**: Operate the Service through an anonymous Firebase account or optional Apple-linked account, apply rate limits, and protect the backend from fraud, abuse, and automated misuse
- **Analytics**: Understand screen usage and app actions through HeyCatch. Guest events use an anonymous SDK identifier; after Apple sign-in, events are linked to your Firebase account identifier (see §5.7).
- **Purchase Entitlement and Restoration**: Verify App Store purchases, maintain subscription entitlement status via RevenueCat subscription event processing, prevent duplicate entitlement from one App Store subscription, and support restoration if you reinstall or change devices

## 4. No Advertising or Tracking

**We do not display advertisements in the App.** Starting with version 1.4.2, the App does not include any advertising SDK (such as Google AdMob), does not collect advertising identifiers (IDFA), and does not use the App Tracking Transparency framework. We do not track users across apps or websites owned by other companies for advertising purposes, and we do not share data with advertising networks.

## 5. Third-Party Services

### 5.1 Google Gemini

- **Purpose**: Your conversation transcripts are sent to Google Gemini to generate Bible reference suggestions and spiritual guidance. When the Mercy Timeline feature is enabled, stored transcripts are also transmitted to Google in batches (at most once per 24 hours) for longitudinal pattern analysis
- **Data Shared**: Conversation text, device context, and user locale. For Mercy Timeline: batches of stored Personal Reflection and Devotion Journey transcripts
- **Session Metadata for Personalization**: When you use generated-response features, the app also sends a small whitelisted session-metadata object alongside your transcript. The fields are: faith stage (the option you chose during onboarding), current streak count, lifetime reflection count, depth tier (a derived integer summarizing your usage history), the time-of-day / day-of-week bucket from your local clock, optional recent reflection-theme tags (e.g. "hope", "grief") drawn from your stored entries, your onboarding goal, address-style preference, life-season tag, and focus-area tag. Your first name is included only when you explicitly chose "By first name" during onboarding. This metadata is processed only to make the response feel personally targeted (for example, a scripture chosen for the part of day you opened the app, or a prayer that uses your name). The metadata is not retained server-side after the response is generated, is not used for advertising or profiling, and does not include free-text content beyond your first name. It does not include your birth date or precise location. You can opt out of name-based address at any time by re-running onboarding or clearing your profile from Profile → Manage My Data
- **Google's Retention**: Google may retain transmitted transcripts and use them to improve their services according to their own privacy policy. We have no control over Google's retention or use of data after transmission
- **Privacy Policy**: [Google Privacy Policy](https://policies.google.com/privacy)
- **Note**: Once data is transmitted to Google, it is subject to Google's privacy policy. If you have concerns about a specific reflection, delete its transcript before the next Mercy Timeline analysis window (Profile → Manage My Data → Clear Transcript Data)

### 5.2 Firebase (Google)

- **Purpose**: Backend services, anonymous authentication, optional Apple-linked authentication, and App Check security
- **Data Shared**: Anonymous Firebase UID, device ID, app version, authentication tokens, and account-linked operational records such as purchase entitlements, usage and first-reflection records, daily guided-reply allowance counters, and devotion state
- **Privacy Policy**: [Firebase Privacy Policy](https://firebase.google.com/support/privacy)

### 5.3 Apple App Store (In-App Purchases)

- **Purpose**: Processing of in-app purchases for Plus subscriptions, subscription management, cancellation/renewal status, restoration, and any legacy restorable entitlements still supported by the Service
- **Data Shared**: Purchase transactions, product identifiers, original transaction identifiers, subscription expiration/status information, and verification data are processed by Apple; RevenueCat processes Apple subscription notifications and purchase records, and our backend reconciles your entitlement from RevenueCat
- **Privacy Policy**: [Apple Privacy Policy](https://www.apple.com/privacy/)

### 5.4 Apple Sign In

- **Purpose**: Optional user authentication that links your app account to your Apple ID for account and operational devotion-state continuity across reinstalls or supported devices. It does not back up device-only journal entries, transcripts or Walk With history. App Store purchase restoration is based on Apple's purchase records and does not require manual Sign in with Apple, although signing in may make account continuity easier
- **Data Shared**: Authentication tokens, basic profile information (if you choose to share with the App)
- **Token Revocation on Account Deletion**: In the current app, signing in does not store a new Apple refresh token on our backend. When you delete an Apple-linked account, the App asks Apple to confirm again and sends the fresh, short-lived authorization code to our backend solely to revoke your Sign in with Apple grant. Cancelling that confirmation cancels deletion. Older app versions may have stored an encrypted Apple refresh token for revocation; existing tokens remain a fallback and are removed during account deletion. Apple revocation is best-effort: if Apple is unreachable, deletion still proceeds
- **Privacy Policy**: [Apple Privacy Policy](https://www.apple.com/privacy/)

### 5.5 RevenueCat

- **Purpose**: Purchase processing, subscription restoration, customer support and entitlement management. RevenueCat receives Apple subscription lifecycle events and manages receipt transfers. Our backend reads RevenueCat subscription records to reconcile your Plus entitlement; the app refreshes that status when needed. Restoration follows the Apple Account used for App Store purchases, which may differ from your optional Sign in with Apple account
- **Data Shared**: Apple original transaction identifiers, product identifiers, subscription status, and your Firebase App User ID. RevenueCat does not receive your voice transcripts, conversation text, or reflection content
- **Privacy Policy**: [RevenueCat Privacy Policy](https://www.revenuecat.com/privacy/)

### 5.6 Error Reporting

- **Purpose**: Capture application errors for debugging and stability improvements
- **Data Shared**: In the current release, the App logs errors only in local debug output and does not send crash data to a third-party crash analytics provider
- **Future Changes**: If off-device crash reporting is enabled in a future release, this Privacy Policy and any applicable platform disclosures will be updated before rollout

### 5.7 HeyCatch Analytics

- **Purpose**: Understand screen usage and app actions to improve the App
- **Data Shared**: Named screens, app-action events, limited counts and settings, and SDK app/device/session metadata. Guests use an anonymous SDK identifier. After Apple sign-in, the Firebase UID links activity to the account; we do not send your name or email. The PostHog open-source SDK sends these records to HeyCatch at `in.heycatch.ai`
- **Excluded**: Voice recordings, transcripts, reflection/prayer/conversation text, crisis events, and the onboarding goal, faith-stage and focus-area answers. Session replay, surveys, automatic tap capture, push capture and automatic error capture are disabled
- **Identity and deletion**: Sign-out and account deletion reset the on-device analytics identity. Resetting does not erase events already received by HeyCatch. Contact jesussays889@gmail.com to request erasure of those records

## 6. Data Storage and Security

- **Local Storage (Your Device)**: Conversation history, reflection and devotion response cards, saved verses, and voice transcripts are stored locally on your device using iOS Keychain encryption (FlutterSecureStorage). Personal Reflection and Devotion Journey entries are stored in a unified journal (Keychain key `journal_entries_device_v2`, capped at 300 entries). Verse Library entries are stored with Keychain `synchronizable: true`, so they may sync through your own iCloud Keychain settings. Listen Mode uses local text-to-speech and does not transmit playback audio. If you updated from an older version, existing entries in the legacy `DEVOTION_HISTORY` and `confession_entries` Keychain keys were automatically migrated to the unified store at first launch. Bible text for in-app verse display is loaded from bundled app resources and is never transmitted to our servers. Voice transcripts from Personal Reflection and Devotion Journey features are also retained separately in encrypted storage to support Mercy Timeline — you may delete them independently via Profile → Manage My Data → Clear Transcript Data. **Voice transcripts are explicitly device-local: they are stored with iCloud Keychain sync disabled, so they do not propagate to your other devices**
- **Apple-Managed Sync (Optional)**: Saved Scripture may synchronize through your own iCloud Keychain account. Journal entries and personal transcripts are stored with sync disabled. This version first copies older synced journal entries to device-only storage, then removes the old synced journal copy after a successful local write. Apple controls sync timing; older app versions on other devices may still retain copies. We cannot erase copies outside the app or guarantee when Apple propagates a deletion.
- **Cloud Storage (Our Backend)**: Authentication tokens, App Check data, and operational records (purchase entitlements, subscription and purchase event records, devotion plans/progress, usage and first-reflection records, daily allowance counters, request-security records and account-deletion markers) are stored securely via Firebase. We do **not** store conversation history or voice transcripts on our own backend servers after generated responses are created
- **Third-Party Processing (Google)**: Conversation text is transmitted to Google Gemini for real-time response generation. When Mercy Timeline is enabled, stored transcripts are also transmitted to Google in batches for pattern analysis. In both cases, Google processes and may retain this data according to their own privacy policy (see §5.1). We do not control Google's retention
- **Security**: We use iOS Keychain encryption for all sensitive on-device data, HTTPS for all network requests, Firebase security rules, and App Check token validation on all backend endpoints. No method of transmission over the internet is 100% secure

## 7. Data Retention

- **Voice Transcripts (Personal Reflection & Devotion Journey)**: Stored on your device in encrypted Keychain storage with iCloud Keychain sync disabled and retained to support Mercy Timeline. Raw transcripts do not sync across your Apple devices. You have the following deletion options:
  - **Delete transcripts, keep reflection cards**: Profile → Manage My Data → Clear Transcript Data (removes raw voice data; your reflection responses and spiritual history remain intact)
  - **Delete your account/session**: Profile → Manage My Data → Delete Account or Delete Session & Data (clears local personal data and requests backend cleanup, as described below)
  - Transcripts already transmitted to Google before a deletion request may be retained by Google according to their policy — we cannot delete Google's copy
- **Talk to Jesus Conversations**: Not stored on our servers after the response is generated. Stored locally if you choose to keep conversation history
- **Account Data**: Retained in Firebase for as long as your account is active (anonymous-account records, optional Apple-linked account records, purchase entitlements, RevenueCat event records, any retained legacy purchase/ownership records, devotion plans/progress, usage and first-reflection records, daily allowance counters). All signed-in users — including anonymous Firebase accounts — may request deletion via **Profile → Manage My Data** in the App. Anonymous users see "Delete Session & Data"; Apple-linked users see "Delete Account". A successful in-app request removes your authentication record immediately and attempts to remove associated backend records. If a storage service is unavailable, cleanup may remain incomplete after the account is deleted; contact jesussays889@gmail.com to request completion. A minimal deletion marker is retained to prevent later subscription events from recreating the account. Request-security nonces are not linked to an account and carry separate expiration timestamps. Deletion does not cancel an App Store subscription.
- **Guest Sessions**: Operational records are retained for anonymous sessions as well as Apple-linked accounts. Reinstalling without first deleting a guest session does not delete those backend records; there is currently no automatic cleanup for abandoned guest sessions. Transcripts, journal entries and conversation history remain local, apart from the processing described above.
- **Analytics Data**: Guest events use an anonymous SDK identifier; signed-in events are linked to a Firebase UID. Previously transmitted records are not erased by resetting the app. Contact us to request erasure (see §5.7).

## 8. Your Rights

You have the right to:
- **Access**: Request access to your personal data, including what transcripts are stored on your device and what operational data Firebase holds
- **Deletion**: All signed-in users may request deletion of their session and associated backend data. Use **Profile → Manage My Data → Delete Session & Data** (anonymous users) or **Profile → Manage My Data → Delete Account** (Apple-linked users). In-app requests run immediately; backend cleanup limitations are described in §7. You may also email jesussays889@gmail.com with the subject "Delete My Account" to request deletion or completion of cleanup (email requests processed within 30 days). To delete only transcripts while keeping your reflection history, use Profile → Manage My Data → Clear Transcript Data
- **Correction**: Request correction of inaccurate data by contacting jesussays889@gmail.com
- **Opt-out of Mercy Timeline (if available)**: Disable the Mercy Timeline feature in the App's Profile at any time to prevent future batch transmission of transcripts to Google. The cached analysis is deleted and the Timeline card is hidden; no new transmissions occur

## 8.1 GDPR (EEA/UK) Rights and Legal Basis

If you are in the European Economic Area (EEA) or United Kingdom:

- **Legal Basis**: We process your data based on your consent (Article 6(1)(a)) — including consent for Mercy Timeline batch transmission to Google — and our legitimate interests in operating and securing the Service (Article 6(1)(f)). You may withdraw consent for Mercy Timeline batch transmission by disabling the feature in the App's Profile, without affecting your ability to use core app features
- **Right to Access**: Request a copy of your personal data
- **Right to Rectification**: Request correction of inaccurate data
- **Right to Erasure**: Request deletion of your data
- **Right to Restrict Processing**: Request temporary restriction of processing in certain circumstances
- **Right to Data Portability**: Request your data in a portable format where legally applicable. Journal entries remain in encrypted storage on the current device. Raw voice transcripts remain on the device and are not synced through iCloud Keychain or retained as history on our backend
- **Right to Object**: Object to certain processing where applicable under local law
- **Right to Withdraw Consent**: Withdraw consent at any time, without affecting prior lawful processing
- **Supervisory Authority**: You may lodge a complaint with your local data protection authority

For GDPR and other data rights requests, contact jesussays889@gmail.com.

## 8.2 California Users (CCPA)

If you are a California resident, you have the following rights under the California Consumer Privacy Act:

- **Right to Know**: You may request what personal information we collect, including voice transcripts stored on your device and any generated patterns created by Mercy Timeline
- **Right to Delete**: You may request deletion of your personal information via Profile → Manage My Data → Delete Account or Delete Session & Data (account/session) or Profile → Manage My Data → Clear Transcript Data (transcripts only). In-app delete requests run immediately as soon as you confirm; backend cleanup limitations are described in §7. Email requests sent to jesussays889@gmail.com are processed within 45 days
- **Right to Opt Out**: We do not sell personal information. You may disable Mercy Timeline in the App's Profile to prevent future transcript transmission to Google
- **Right to Non-Discrimination**: Exercising your CCPA rights will not affect your access to the Service

To exercise these rights, contact jesussays889@gmail.com or use the data controls in the App's Profile.

## 9. Children's Privacy

The App is not intended for children under the age of 13. We do not knowingly collect personal information from children under 13. If you believe we have collected information from a child under 13, please contact us immediately.

## 10. International Data Transfers

Your information may be transferred to and processed in countries other than your country of residence. These countries may have data protection laws that differ from those in your country.

## 11. Changes to This Privacy Policy

We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy in the App and updating the "Last Updated" date.

## 12. Generated Content and Data Usage

**Important Notice:**
- Your conversations are processed by Google Gemini to generate responses and scripture references
- Google may use this data to improve its services according to its privacy policy
- We do not control how Google processes your conversation data
- Generated responses are not reviewed or approved by us before being shown to you
- Scripture text shown in the App is resolved from the bundled English KJV Bible asset rather than being quoted directly from the model

## 12.1 Mercy Timeline — Pattern Analysis Across Your Reflections

Mercy Timeline is disabled in the default 2.2.1 release. No Timeline batch analysis runs while it is disabled. The following describes its data handling only if it is made available and you enable it. Its controls are shown only when the feature is available.

The Mercy Timeline feature (Plus subscribers, 10+ qualifying spoken reflections of at least ~20 words each) analyzes your Personal Reflection and Devotion Journey transcripts over time to surface recurring themes, notable shifts in spiritual tone, and what seems resolved.

**How your data is used:**
- Transcripts are stored on your device in encrypted Keychain storage and retained until you delete them
- At most once every 24 hours, stored transcripts are transmitted to Google's Gemini API as a batch for pattern analysis
- Google processes and may retain these transcripts according to their own privacy policy ([Google Privacy Policy](https://policies.google.com/privacy))
- We do not store raw transcripts on our backend servers after the analysis completes
- Analysis results are cached on your device only

**Important limitations:**
- Mercy Timeline is **not a clinical assessment**. It is a spiritual reflection tool
- Analysis is generated and is **not reviewed by licensed clinical professionals**
- Patterns identified may be inaccurate or misinterpreted
- Do **not** use Mercy Timeline results for medical, clinical, or crisis decisions

**Your control:**
- Disable Mercy Timeline: Profile → Manage My Data → Mercy Timeline — prevents future batch transmissions, deletes cached analysis, and hides the Timeline card
- Delete transcripts: Profile → Manage My Data → Clear Transcript Data — removes on-device copies; Google's copies subject to their policy
- Delete everything: Profile → Manage My Data → Delete Account

## 13. Clinical Care & Crisis Resources

Jesus Says is a spiritual guidance app and is **not** a substitute for professional clinical care or crisis intervention. Generated responses are not reviewed by licensed clinical professionals. If you or someone you know needs immediate help, please contact:

- **988 Suicide & Crisis Lifeline**: Call or text **988** (US) — [988lifeline.org](https://988lifeline.org)
- **Crisis Text Line**: Text **HOME** to **741741** — [crisistextline.org](https://www.crisistextline.org)
- **Emergency Services**: Call **911** (US) or your local emergency number

## 14. Contact Us

If you have questions about this Privacy Policy, please contact us at:
- Email: jesussays889@gmail.com

## 15. Consent

By using the App, you consent to:
- The collection and use of your information, including anonymous-account data, as described in this Privacy Policy
- The sharing of your conversation data with Google Gemini
- The use of third-party services (Firebase, Apple App Store, and authentication providers)

---

**By using Jesus Says, you acknowledge that you have read and understood this Privacy Policy, including how your data is shared with third-party services like Google Gemini.**
