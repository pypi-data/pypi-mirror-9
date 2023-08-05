## 2.1.0

- Support non-JSON data for, e.g., creating uploads
- Add `sort_by` common parameter
- Regenerate API from updated mirror. See [full
  commit](https://github.com/fprimex/zdesk/commit/cbeb1ecd0ae4580caa3ad434c74e7e49d4378c19)
- Update `examples/__init__.py` with fixes and ticket updates and uploads
- Reorder CHANGELOG.md with most recent releases at top

## 2.0.3

- Add `get_all_pages` option to call to exhaustively follow `next_page`
- Combine and reduce multiple requests when using `get_all_pages`

## 2.0.2

- Always inject auth credentials into request when they are supplied

## 2.0.1

- Immediately fix import bug in 2.0.0

## 2.0.0

- Drop APIv1 support code completely
- Drop endpoints dicts for new API generator approach
- Support Python 2 and Python 3 in codebase without 2to3 translation

## 1.2.0

- Fork zendesk from eventbrite
- Merge PRs and apply fixes
- Python 3 compatibility

