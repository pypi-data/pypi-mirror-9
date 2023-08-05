# Release Notes

## Unreleased

## 0.5.0 (2015-01-07)

* `pycobertura diff` HTML output now only includes hunks of lines that have
  coverage changes and skips unchanged classes
* handle asymmetric presence of classes in the reports (regression
  introduced in 0.4.0)
* introduce `CoberturaDiff.diff_missed_lines()`
* introduce `CoberturaDiff.classes()`
* introduce `CoberturaDiff.filename()`
* introduce `Cobertura.filepath()` which will return the system path to the
  file. It uses `base_path` to resolve the path.
* the summary table of `pycobertura diff` no longer shows classes that are no
  longer present
* `Cobertura.filename()` now only returns the filename of the class as found in
  the Cobertura report, any `base_path` computation is omitted.
* Argument `xml_source` of `Cobertura.__init__()` is renamed to `xml_path` and
  only accepts an XML path because much of the logic involved in source code
  path resolution is based on the path provided which cannot work with file
  objects or XML strings.
* Rename `Cobertura.source` -> `Cobertura.xml_path`
* `pycobertura diff` now takes options `--missed` (default) or `--no-missed` to
  show missed line numbers. If `--missed` is given, the paths to the source
  code must be accessible.

## 0.4.1 (2015-01-05)

* return non-zero exit code if uncovered lines rises (previously based on line
  rate)

## 0.4.0 (2015-01-04)

* rename `Cobertura.total_lines()` -> `Cobertura.total_statements()`
* rename `Cobertura.line_hits()` -> `Cobertura.hit_statements()`
* introduce `Cobertura.missed_statements()`
* introduce `Cobertura.line_statuses()` which returns line numbers for a
  given class name with hit/miss statuses
* introduce `Cobertura.class_source()` which returns the source code for a
  given class along with hit/miss status
* `pycobertura show` now includes HTML source
* `pycobertura show` now accepts `--source` which indicates where the source
  code directory is located
* `Cobertura()` now takes an optional `base_path` argument which will be used
  to resolve the path to the source code by joining the `base_path` value to
  the path found in the Cobertura report.
* an error is now raised if `Cobertura` is passed a non-existent XML file path
* `pycobertura diff` now includes HTML source
* `pycobertura diff` now accepts `--source1` and `--source2` which indicates
  where the source code directory of each of the Cobertura reports are located
* introduce `CoberturaDiff` used to diff `Cobertura` objects
* argument `class_name` for `Cobertura.total_statements` is now optional
* argument `class_name` for `Cobertura.total_misses` is now optional
* argument `class_name` for `Cobertura.total_hits` is now optional

## 0.3.0 (2014-12-23)

* update description of pycobertura
* pep8-ify
* add pep8 tasks for tox and travis
* diff command returns non-zero exit code if coverage worsened
* `Cobertura.branch_rate` is now a method that can take an optional
  `class_name` argument
* refactor internals for improved readability
* show classes that contain no lines, e.g. `__init__.py`
* add `Cobertura.filename(class_name)` to retrieve the filename of a class
* fix erroneous reporting of missing lines which was equal to the number of
  missed statements (wrong because of multiline statements)

## 0.2.1 (2014-12-10)

* fix py26 compatibility by switching the XML parser to `lxml` which has a more
  predictible behavior when used across all Python versions.
* add Travis CI

## 0.2.0 (2014-12-10)

* apply Skeleton 2.0 theme to html output
* add `-o` / `--output` option to write reports to a file.
* known issue: diffing 2 files with options `--format text`, `--color` and
  `--output` does not render color under PY2.

## 0.1.0 (2014-12-03)

* add `--color` and `--no-color` options to `pycobertura diff`.
* add option `-f` and `--format` with output of `text` (default) and `html`.
* change class naming from `report` to `reporter`

## 0.0.2 (2014-11-27)

* MIT license
* use pypandoc to convert the `long_description` in setup.py from Markdown to
  reStructuredText so pypi can digest and format the pycobertura page properly.

## 0.0.1 (2014-11-24)

* Initial version
