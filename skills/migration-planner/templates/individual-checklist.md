# Leaving a provider / moving your stuff — personal checklist

For when you're moving your own email, files, accounts or devices off one service onto another. The whole method shrinks to this. Tick in order; the order matters.

## Before you move anything
- [ ] **Make a backup** of what you're moving, somewhere separate. Open a few files to confirm it's real.
- [ ] List what you're moving and **what depends on your old account** — especially anything that uses your old email for login or password recovery (bank, taxes, government, shopping, social).

## Email
- [ ] Set up the new mailbox.
- [ ] Copy old mail across (provider import tool, or `imapsync`).
- [ ] Check the counts look right; open some old messages; send and receive a test.
- [ ] Set the old account to **forward** to the new one (don't delete it yet).
- [ ] Update your address with the people and services that matter.

## Accounts, passwords, 2FA  (do this before closing anything)
- [ ] Export from the old password manager, import to the new one.
- [ ] For important accounts, **change the recovery email/phone to the new one.**
- [ ] Re-enrol 2FA / passkeys on the critical accounts (the codes don't transfer).
- [ ] Rotate any API keys / SSH keys if the old store is leaving your control.

## Files & photos
- [ ] Copy everything to the new place (`rclone`/`rsync`, or the provider's tool).
- [ ] Compare file count and total size old vs new; open a sample.
- [ ] Check shared links/permissions you care about still work (they often don't survive — re-share).

## Subscriptions & cleanup
- [ ] Note what you pay the old provider and when it renews.
- [ ] Cancel the things you're retiring (the trials, the duplicates).

## Only after everything above is verified
- [ ] Live on the new setup for **a week or two** with the old one still around.
- [ ] Confirm nothing still uses the old email/account for recovery.
- [ ] **Then** close/delete the old account. ⚠ This is the one-way door — last, not first.

## Domain or phone number involved?
- [ ] Don't cancel the old service to free it — **port/transfer** it instead, and don't cancel until the port completes (cancelling can kill the transfer).
- [ ] Expect a short lead time you don't fully control.
