import lxml.etree as ET
import os

from pycobertura.utils import (
    extrapolate_coverage,
    reconcile_lines,
    hunkify_lines,
)


class Cobertura(object):
    """
    An XML cobertura parser.
    """
    def __init__(self, xml_path, base_path=None):
        """
        Initialize a Cobertura report given a path to an XML file `xml_path`
        that is in the cobertura format.

        The optional argument `base_path` can be provided to resolve the path
        to the source code. If omitted, `base_path` will be set to
        `os.path.dirname(xml_source)`.
        """
        if base_path is None:
            base_path = os.path.dirname(xml_path)

        self.base_path = base_path
        self.xml_path = xml_path
        self.xml = ET.parse(xml_path).getroot()

    def _get_element_by_class_name(self, class_name):
        syntax = "./packages/package/classes/class[@name='%s'][1]" % class_name
        return self.xml.xpath(syntax)[0]

    def _get_lines_by_class_name(self, class_name):
        el = self._get_element_by_class_name(class_name)
        return el.xpath('./lines/line')

    @property
    def version(self):
        """Return the version number of the coverage report."""
        return self.xml.attrib['version']

    def line_rate(self, class_name=None):
        """
        Return the global line rate of the coverage report. If the class
        `class_name` is given, return the line rate of the class.
        """
        if class_name is None:
            el = self.xml
        else:
            el = self._get_element_by_class_name(class_name)

        return float(el.attrib['line-rate'])

    def branch_rate(self, class_name=None):
        """
        Return the global branch rate of the coverage report. If the class
        `class_name` is given, return the branch rate of the class.
        """
        if class_name is None:
            el = self.xml
        else:
            el = self._get_element_by_class_name(class_name)

        return float(el.attrib['branch-rate'])

    def missed_statements(self, class_name):
        """
        Return a list of uncovered line numbers for each of the missed
        statements found for the class `class_name`.
        """
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits=0]')
        return [int(l.attrib['number']) for l in lines]

    def hit_statements(self, class_name):
        """
        Return a list of covered line numbers for each of the hit statements
        found for the class `class_name`.
        """
        el = self._get_element_by_class_name(class_name)
        lines = el.xpath('./lines/line[@hits>0]')
        return [int(l.attrib['number']) for l in lines]

    def line_statuses(self, class_name):
        """
        Return a list of tuples `(lineno, status)` of all the lines found in
        the Cobertura report where `lineno` is the line number and `status` is
        coverage status of the line which can be either `True` (line hit) or
        `False` (line miss).
        """
        line_elements = self._get_lines_by_class_name(class_name)

        lines_w_status = []
        for line in line_elements:
            lineno = int(line.attrib['number'])
            status = line.attrib['hits'] != '0'
            lines_w_status.append((lineno, status))

        return lines_w_status

    def missed_lines(self, class_name):
        """
        Return a list of extrapolated uncovered line numbers according to
        `Cobertura.line_statuses`.
        """
        statuses = self.line_statuses(class_name)
        statuses = extrapolate_coverage(statuses)
        return [lno for lno, status in statuses if status is False]

    def class_source(self, class_name):
        """
        Return a list of 3-element tuples `(lineno, source, status)` for each
        lines of code found in the source file of the class `class_name`.

        The 3 elements in each tuple are:
        `lineno`: line number in the source code
        `source`: actual source code for line number `lineno`
        `status`: True (hit) or False (miss)
        """
        filename = self.filepath(class_name)

        if not os.path.exists(filename):
            return [(0, '%s not found' % filename, None)]

        with open(filename) as f:
            lines = []
            line_statuses = dict(self.line_statuses(class_name))
            for lineno, source in enumerate(f, start=1):
                line_status = line_statuses.get(lineno)
                lines.append((lineno, source, line_status))

        return lines

    def total_misses(self, class_name=None):
        """
        Return the total number of uncovered statements for the class
        `class_name`. If `class_name` is not given, return the total number of
        uncovered statements for all classes.
        """
        if class_name is not None:
            return len(self.missed_statements(class_name))

        total = 0
        for class_name in self.classes():
            total += len(self.missed_statements(class_name))

        return total

    def total_hits(self, class_name=None):
        """
        Return the total number of covered statements for the class
        `class_name`. If `class_name` is not given, return the total number of
        covered statements for all classes.
        """
        if class_name is not None:
            return len(self.hit_statements(class_name))

        total = 0
        for class_name in self.classes():
            total += len(self.hit_statements(class_name))

        return total

    def total_statements(self, class_name=None):
        """
        Return the total number of statements for the class `class_name`. If
        `class_name` is not given, return the total number of statements for
        all classes.
        """
        if class_name is not None:
            statements = self._get_lines_by_class_name(class_name)
            return len(statements)

        total = 0
        for class_name in self.classes():
            statements = self._get_lines_by_class_name(class_name)
            total += len(statements)

        return total

    def filename(self, class_name):
        """
        Return the filename of the class `class_name` as found in the Cobertura
        report.
        """
        el = self._get_element_by_class_name(class_name)
        filename = el.attrib['filename']
        return filename

    def filepath(self, class_name):
        """
        Return the filesystem path to the actual class file. It uses the
        `base_path` value initialized in the constructor by prefixing it to the
        class filename using `os.path.join(base_path, filename)`.
        """
        filename = self.filename(class_name)
        filepath = os.path.join(self.base_path, filename)
        return filepath

    def classes(self):
        """
        Return the list of available classes in the coverage report.
        """
        return [el.attrib['name'] for el in self.xml.xpath("//class")]

    def has_class(self, class_name):
        """
        Return `True` if the class `class_name` is present in the report,
        return `False` otherwise.
        """
        # FIXME: this will lookup a list which is slow, make it O(1)
        return class_name in self.classes()

    def class_lines(self, class_name):
        """
        Return a list for source lines of class `class_name`.
        """
        with open(self.filepath(class_name)) as f:
            return f.readlines()

    def packages(self):
        """
        Return the list of available packages in the coverage report.
        """
        return [el.attrib['name'] for el in self.xml.xpath("//package")]


class CoberturaDiff(object):
    """
    Diff Cobertura objects.
    """
    def __init__(self, cobertura1, cobertura2):
        self.cobertura1 = cobertura1
        self.cobertura2 = cobertura2

    def has_all_changes_covered(self):
        """
        Return `True` if all changes in the diff are covered, `False`
        otherwise.

        This goes over every individual classes and checks whether missed
        statements are present. Looking at the just the total missed statements
        would be inaccurate since it could still include uncovered lines.
        """
        for class_name in self.classes():
            if self.diff_total_misses(class_name) > 0:
                return False
        return True

    def _diff_attr(self, attr_name, class_name):
        """
        Return the difference between `self.cobertura2.<attr_name>(class_name)`
        and `self.cobertura1.<attr_name>(class_name)`.

        This generic method is meant to diff the count of methods that return
        counts for a given class name, e.g. `Cobertura.total_statements`,
        `Cobertura.total_misses`, ...

        The returned count may be a float.
        """
        if class_name is not None:
            classes = [class_name]
        else:
            classes = self.classes()

        total_count = 0.0
        for class_name in classes:
            if self.cobertura1.has_class(class_name):
                method = getattr(self.cobertura1, attr_name)
                count1 = method(class_name)
            else:
                count1 = 0.0
            method = getattr(self.cobertura2, attr_name)
            count2 = method(class_name)
            total_count += count2 - count1

        return total_count

    def diff_total_statements(self, class_name=None):
        return int(self._diff_attr('total_statements', class_name))

    def diff_total_misses(self, class_name=None):
        return int(self._diff_attr('total_misses', class_name))

    def diff_total_hits(self, class_name=None):
        return int(self._diff_attr('total_hits', class_name))

    def diff_line_rate(self, class_name=None):
        return self._diff_attr('line_rate', class_name)

    def diff_missed_lines(self, class_name):
        """
        Return a list of 2-element tuples `(lineno, is_new)` where `lineno` is
        a missed line number and `is_new` indicates whether the missed line was
        introduced (True) or removed (False).
        """
        line_changed = []
        for lineno, line, status in self.class_source(class_name):
            if status is not None:
                is_new = not status
                line_changed.append((lineno, is_new))
        return line_changed

    def classes(self):
        """
        Return `self.cobertura2.classes()`.
        """
        return self.cobertura2.classes()

    def filename(self, class_name):
        """
        Return `self.cobertura2.filename(class_name)`.
        """
        return self.cobertura2.filename(class_name)

    def class_source(self, class_name):
        """
        Return a list of 3-element tuples `(lineno, source, status)` for each
        lines of code found in the source file of the class `class_name`.

        The 3 elements in each tuple are:
        `lineno`: line number in the source code
        `source`: actual source code for line number `lineno`
        `status`: True (hit), False (miss) or None (coverage unchanged)
        """
        if self.cobertura1.has_class(class_name):
            lines1 = self.cobertura1.class_lines(class_name)
            line_statuses1 = dict(self.cobertura1.line_statuses(class_name))
        else:
            lines1 = []
            line_statuses1 = {}

#            if not os.path.exists(filename):
#                return [(0, '%s not found' % filename, None)]

        lines2 = self.cobertura2.class_lines(class_name)
        line_statuses2 = dict(self.cobertura2.line_statuses(class_name))

        # Build a dict of lineno2 -> lineno1
        lineno_map = reconcile_lines(lines2, lines1)

        lines = []
        for lineno, line in enumerate(lines2, start=1):

            if lineno not in lineno_map:
                # line was added or removed, just use whatever coverage status
                # is available as there is nothing to compare against.
                line_status = line_statuses2.get(lineno)
            else:
                other_lineno = lineno_map[lineno]
                line_status1 = line_statuses1.get(other_lineno)
                line_status2 = line_statuses2.get(lineno)
                if line_status1 is line_status2:
                    line_status = None  # unchanged
                elif line_status1 is True and line_status2 is False:
                    line_status = False  # decreased
                elif line_status1 is False and line_status2 is True:
                    line_status = True  # increased

            lines.append((lineno, line, line_status))

        return lines

    def class_source_hunks(self, class_name):
        """
        Like `CoberturaDiff.class_source`, but returns a list of line hunks of
        the lines that have changed. An empty list means that the class has no
        lines that have a change in coverage status.
        """
        lines = self.class_source(class_name)
        hunks = hunkify_lines(lines)
        return hunks
