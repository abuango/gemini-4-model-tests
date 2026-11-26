# Ledger settlement

Write `settle(events)` in `ledger.py`, using only the Python standard library. `events` is a list of dicts in the order they were recorded. Each has `op` and `t` (the day it was recorded, an integer that never decreases). Amounts are integers. Return the report in section 9. Never modify `events`.

## 1. Terms
- Period p covers days 30p to 30p+29. Every period is open until it is closed. "The earliest open period" is the lowest-numbered period that is not closed, starting from 0.
- An entry has an id, an account, an amount (positive adds to the account, negative takes from it), an effective day, and a category. An entry is live unless it has been removed. An entry is closed if its effective day is in a closed period.
- The balance of an account is the sum of all its live entries, whatever their effective day.
- The floor is 0 for a `prepaid` account and minus the limit for a `credit` account.
- The available amount of an account is its balance minus its active holds minus its floor. A hold is active while it has not been captured and the current event's `t` is at most its `exp`.
- A funds check for an amount x < 0 passes if available + x >= 0. A funds check for x >= 0 always passes.
- The effective day of a new entry is the requested day, unless that day is in a closed period. In that case it is the first day of the earliest open period.
- Round half to even wherever rounding is mentioned, unless a rule says otherwise. All arithmetic must be exact.
- A rejected event changes nothing except that `[key, code]` is added to the rejects. The key is the event's `id`; for `open` it is the account, and for `close` it is the period number as a string. Checks run in the order they are listed, and the first failure decides the code.
- Every id used by an accepted `post`, `transfer`, `split`, `hold` or `capture` is taken, and an event that brings a taken id is rejected with `dup`. This is checked first. Rejected events don't take their id.

## 2. open: `acct`, `kind`, `limit`
Creates the account. Reject with `dup` if it exists. `limit` is ignored for `prepaid`.

## 3. post: `id`, `acct`, `amt`, `eff`, `cat`
Reject with `acct` if the account doesn't exist, then with `funds` if the funds check for `amt` fails. Category `fee` skips the funds check.

## 4. split: `id`, `acct`, `amt`, `eff`, `weights`
Divides `amt` in proportion to the weights into entries `id#0`, `id#1` and so on, with category `split`. Give each part the whole number at or below its exact share of the absolute amount. Hand out the units left over one at a time, in order of largest fractional remainder, with ties going to the lower index. Then apply the sign of `amt`. Parts of 0 still create an entry. Reject with `acct`, then with `funds` (checked once, on the whole amount).

## 5. transfer: `id`, `src`, `dst`, `amt` (> 0), `eff`
Creates `id.s` (-amt on src), `id.d` (+amt on dst), both with category `xfer`, and `id.f` on src with category `fee`. The fee is 0.7% of amt, rounded, at least 1. Reject with `acct` if either account doesn't exist, then `same` if src is dst, then `funds` if the check on src for -amt fails (the fee is not included in the check), then `cap` if dst is a credit account and its balance after receiving amt would be above its limit.

## 6. amend and reverse
- `amend`: `id` (of an entry), `amt`. Reject with `state` if there is no such live entry, if it has been reversed, or if it is an adjustment, a contra, a capture, or an entry created by `close`. Then reject with `funds` if the check for (new amount minus current amount) fails. The current amount of an entry is its original amount plus all its adjustments. Category `fee` skips the funds check. If the entry is open, its own amount changes so that the current amount equals `amt`. If it is closed, add an adjustment entry `id~k` for the difference, where k is 1 for the first adjustment of that entry, then 2, and so on. Its requested day is `t`, it goes on the same account, and it has the category of the entry. An amendment that makes no difference is accepted and creates nothing.
- `reverse`: `id` (of an entry). Reject with `state` under the same conditions as amend, then `funds` if the check for minus the current amount fails. (Category `fee` skips the check.) If the entry is open, remove it and all its adjustments. If it is closed, add a contra entry `id!` for minus the current amount, with requested day `t` and the category of the entry. The entry is now reversed. Any adjustment of a reversed closed entry stays.

## 7. hold and capture
- `hold`: `id`, `acct`, `amt` (> 0), `exp`. Reject with `acct`, then `funds` if the check for -amt fails.
- `capture`: `id`, `hold`, `amt` (> 0). Reject with `hold` if the hold doesn't exist, has been captured, or is past its `exp`, or if amt is more than the hold. Otherwise the hold is captured and the rest of it is released. Adds entry `id` of -amt on the account of the hold, with requested day `t` and category `cap`. There is no funds check.

## 8. close: `period`
Reject with `period` unless it is the earliest open period and t >= 30*(period+1). Then, for each account in alphabetical order, using the entries as they were before this event:
- The closing balance is the sum of its live entries with an effective day up to the last day of the period.
- The average is the sum, over the 30 days of the period, of its end-of-day balance (live entries with an effective day up to that day), divided by 30. Don't round it.
- Credit account with a negative average: interest on its absolute value, at 1% on the first 10000, 1.5% on the next 40000 and 2% on the rest. Add the parts first, then round the total. Charge it as a negative entry `int:p:acct` with category `int`. A result of 0 creates nothing.
- Prepaid account with an average of at least 5000: a bonus of 0.25% of the average, rounded down, as a positive entry `int:p:acct` with category `int`.
- Prepaid account with a closing balance above 0 and no live entry with an effective day in the period other than categories `fee` and `int`: a dormancy fee of 50, or the closing balance if that is lower, as a negative entry `dor:p:acct` with category `fee`.
All entries created by `close` have an effective day on the first day of the next period. After every account is done, the period is closed.

## 9. Report
A dict with:
- `balances`: account to balance, for all accounts.
- `closed`: period number as a string, to a dict of account to closing balance as it was when that period was closed.
- `late`: the number of entries whose effective day was moved because the requested day was in a closed period (counting entries that were later removed).
- `fees`: minus the sum of all live entries with category `fee`.
- `live`: the number of live entries.
- `held`: the sum of holds still active at the `t` of the last event.
- `rejects`: the list of `[key, code]` in order.
