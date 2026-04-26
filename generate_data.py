"""
generate_data.py
Java training-data generator for BugLens AI.

Output path : data/java_data.csv
Rows generated:
  700  buggy          (100 per bug type × 7 types)
  700  clean-from-fix (fixed_code version of every buggy row, is_bug=0, bug_type="clean")
  100  original-clean
  100  extra-clean
Total: 1,600
"""

import csv
import os
import random
from typing import Any

random.seed(42)

LANGUAGE = "java"
OUTPUT_PATH = os.path.join("data", "java_data.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Name pools — large enough so 100 samples per type get real variety
# ─────────────────────────────────────────────────────────────────────────────

_VARS = [
    "value", "result", "data", "item", "element", "entry", "record",
    "node", "target", "source", "output", "input", "buffer", "temp",
    "current", "prev", "next", "first", "last", "token", "key",
    "name", "label", "message", "text", "line", "word", "content",
    "response", "request", "query", "param", "config", "flag", "status",
    "number", "code", "ref", "age", "price", "score", "username", "email",
    "title", "info", "path", "url", "duration", "timeout", "limit",
    "threshold", "capacity", "offset", "pos", "count", "total",
    "sum", "avg", "maxVal", "minVal", "prefix", "suffix", "pattern",
    "fmt", "locale", "region", "tag", "category", "payload", "chunk",
    "segment", "bucket", "slot", "cursor", "iterator", "stream",
    "handle", "descriptor", "pointer", "address", "packet", "frame",
]

_METHODS = [
    "process", "compute", "calculate", "evaluate", "execute", "run",
    "initialize", "setup", "configure", "build", "create", "generate",
    "parse", "convert", "transform", "validate", "verify",
    "read", "write", "load", "save", "store", "fetch", "retrieve",
    "update", "delete", "remove", "insert", "append", "sort", "search",
    "find", "filter", "display", "render", "connect", "send", "receive",
    "encode", "decode", "merge", "split", "copy", "reset", "clear",
    "refresh", "notify", "log", "report", "start", "stop", "pause",
    "check", "scan", "handle", "dispatch", "register",
    "resolve", "normalize", "sanitize", "serialize", "deserialize",
    "publish", "subscribe", "consume", "produce", "flush", "drain",
    "compact", "expand", "compress", "decompress", "index", "query",
]

_CLASSES = [
    "Manager", "Handler", "Processor", "Controller", "Service",
    "Repository", "Provider", "Factory", "Builder", "Adapter",
    "Converter", "Validator", "Parser", "Formatter", "Calculator",
    "Analyzer", "Monitor", "Tracker", "Logger", "Scheduler",
    "Worker", "Runner", "Executor", "Mapper", "Transformer",
    "Resolver", "Collector", "Publisher", "UserService", "DataService",
    "FileHandler", "EventProcessor", "TaskRunner", "CacheManager",
    "ConfigLoader", "RequestHandler", "TokenValidator", "RuleEngine",
    "SessionManager", "OrderProcessor", "PaymentHandler",
    "ReportGenerator", "DataExporter", "BatchProcessor", "Indexer",
    "Coordinator", "Orchestrator", "Aggregator", "Dispatcher",
    "Normalizer", "Tokenizer", "Classifier", "Extractor", "Encoder",
    "Pipeline", "Connector", "Broker", "Router", "Gateway",
]

_FILE_PATHS = [
    '"data.txt"', '"config.json"', '"output.csv"', '"input.xml"',
    '"log.txt"', '"report.txt"', '"settings.ini"', '"records.dat"',
    '"users.csv"', '"products.csv"', '"orders.json"', '"audit.log"',
    '"backup.dat"', '"temp.txt"', '"errors.log"', '"access.log"',
    '"export.csv"', '"import.xml"', '"cache.bin"', '"index.dat"',
]

# Optional comment lines (already double-indented, trailing \n included).
# Empty string = no comment.
_CMTS = [
    "        // process the data\n",
    "        // validate before use\n",
    "        // TODO: add null check\n",
    "        // compute the value\n",
    "        // initialize component\n",
    "        // handle the response\n",
    "        // log the output\n",
    "        // check status first\n",
    "        // retrieve the result\n",
    "        // update the record\n",
    "",
]


# ─────────────────────────────────────────────────────────────────────────────
# Shorthand samplers
# ─────────────────────────────────────────────────────────────────────────────

def _v() -> str:
    return random.choice(_VARS)


def _v2(ex: str = "") -> str:
    return random.choice([x for x in _VARS if x != ex])


def _m() -> str:
    return random.choice(_METHODS)


def _c() -> str:
    return random.choice(_CLASSES)


def _f() -> str:
    return random.choice(_FILE_PATHS)


def _n(lo: int = 3, hi: int = 14) -> int:
    return random.randint(lo, hi)


def _cmt() -> str:
    return random.choice(_CMTS)


def _str_sm() -> str:
    """A String instance method — works inside println (any return type ok)."""
    return random.choice([
        "length()", "toUpperCase()", "toLowerCase()", "trim()",
        "isEmpty()", "charAt(0)", "hashCode()", "indexOf('a')",
        "replace('x', 'y')", "substring(1)",
    ])


def _int_sm() -> str:
    """A String instance method that returns int."""
    return random.choice(["length()", "hashCode()", "indexOf('a')"])


# ─────────────────────────────────────────────────────────────────────────────
# Row factories
# ─────────────────────────────────────────────────────────────────────────────

def _make(
    code: str,
    fixed: str,
    bug_type: str,
    line_number: int,
    description: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "language": LANGUAGE,
        "is_bug": 1,
        "bug_type": bug_type,
        "line_number": line_number,
        "description": description,
        "fixed_code": fixed,
    }


def _to_clean(s: dict[str, Any]) -> dict[str, Any]:
    """Companion clean row: code = fixed_code, is_bug = 0, bug_type = 'clean'."""
    return {
        "code": s["fixed_code"],
        "language": s["language"],
        "is_bug": 0,
        "bug_type": "clean",
        "line_number": 0,
        "description": "No bugs found.",
        "fixed_code": s["fixed_code"],
    }


def _clean(code: str) -> dict[str, Any]:
    return {
        "code": code,
        "language": LANGUAGE,
        "is_bug": 0,
        "bug_type": "clean",
        "line_number": 0,
        "description": "No bugs found.",
        "fixed_code": code,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: null_pointer  (10 structural shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_null_pointer() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — uninitialized private String field, method call in instance method
    for _ in range(10):
        v, m, cls, sm = _v(), _m(), _c(), _str_sm()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    private String {v};\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        System.out.println({v}.{sm});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    private String {v};\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        if ({v} != null) {{\n"
            f"            System.out.println({v}.{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"Field '{v}' is null by default; calling .{sm} causes NullPointerException."))

    # Shape 2 — local variable explicitly assigned null, then dereferenced
    for _ in range(10):
        v, v2, m, cls, sm = _v(), _v(), _m(), _c(), _str_sm()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String {v} = null;\n"
            f"        String {v2} = {v}.{sm};\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String {v} = null;\n"
            f"        if ({v} != null) {{\n"
            f"            String {v2} = {v}.{sm};\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"'{v}' is assigned null and immediately dereferenced via .{sm}."))

    # Shape 3 — private helper returns null; caller uses result without check
    for _ in range(10):
        v, m, m2, cls, sm = _v(), _m(), _m(), _c(), _str_sm()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    private String get{v.capitalize()}() {{\n"
            f"        return null;\n"
            f"    }}\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String result = get{v.capitalize()}();\n"
            f"        System.out.println(result.{sm});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    private String get{v.capitalize()}() {{\n"
            f"        return null;\n"
            f"    }}\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String result = get{v.capitalize()}();\n"
            f"        if (result != null) {{\n"
            f"            System.out.println(result.{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 8 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"get{v.capitalize()}() returns null; result used without null check."))

    # Shape 4 — newly allocated array has null elements; element dereferenced immediately
    for _ in range(10):
        v, m, cls, sm, n = _v(), _m(), _c(), _str_sm(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String[] {v} = new String[{n}];\n"
            f"        System.out.println({v}[0].{sm});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String[] {v} = new String[{n}];\n"
            f"        if ({v}[0] != null) {{\n"
            f"            System.out.println({v}[0].{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"Array '{v}' elements are null by default; {v}[0].{sm} throws NullPointerException."))

    # Shape 5 — null-check guards the wrong variable; different variable dereferenced
    for _ in range(10):
        v, m, cls, sm = _v(), _m(), _c(), _str_sm()
        v2 = _v2(v)
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(String {v}, String {v2}) {{\n"
            f"{cmt}"
            f"        if ({v} != null) {{\n"
            f"            System.out.println({v2}.{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(String {v}, String {v2}) {{\n"
            f"{cmt}"
            f"        if ({v} != null && {v2} != null) {{\n"
            f"            System.out.println({v2}.{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"Null check guards '{v}' but '{v2}' is dereferenced without a guard."))

    # Shape 6 — HashMap.get() returns null; result dereferenced without check
    for _ in range(10):
        v, v2, m, cls, sm = _v(), _v(), _m(), _c(), _str_sm()
        cmt = _cmt()
        buggy = (
            f"import java.util.HashMap;\n"
            f"import java.util.Map;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        Map<String, String> map = new HashMap<>();\n"
            f"{cmt}"
            f"        String {v2} = map.get(\"{v}\");\n"
            f"        System.out.println({v2}.{sm});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.util.HashMap;\n"
            f"import java.util.Map;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        Map<String, String> map = new HashMap<>();\n"
            f"{cmt}"
            f"        String {v2} = map.get(\"{v}\");\n"
            f"        if ({v2} != null) {{\n"
            f"            System.out.println({v2}.{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 8 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"map.get() can return null; '{v2}' used without null check."))

    # Shape 7 — chained method call on a null Object
    for _ in range(10):
        v, v2, m, cls = _v(), _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        Object {v} = null;\n"
            f"        String {v2} = {v}.toString().trim();\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        Object {v} = null;\n"
            f"        if ({v} != null) {{\n"
            f"            String {v2} = {v}.toString().trim();\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"'{v}' is null; calling .toString() on it causes NullPointerException."))

    # Shape 8 — static method receives null parameter, uses without guard
    for _ in range(10):
        v, m, cls, sm = _v(), _m(), _c(), _str_sm()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public static void {m}(String {v}) {{\n"
            f"{cmt}"
            f"        System.out.println({v}.{sm});\n"
            f"    }}\n"
            f"\n"
            f"    public static void main(String[] args) {{\n"
            f"        {m}(null);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public static void {m}(String {v}) {{\n"
            f"{cmt}"
            f"        if ({v} == null) return;\n"
            f"        System.out.println({v}.{sm});\n"
            f"    }}\n"
            f"\n"
            f"    public static void main(String[] args) {{\n"
            f"        {m}(null);\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"Parameter '{v}' may be null; .{sm} called without null guard."))

    # Shape 9 — conditionally assigned string, used unconditionally outside branch
    for _ in range(10):
        v, v2, m, cls, sm, n = _v(), _v(), _m(), _c(), _str_sm(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v2}) {{\n"
            f"{cmt}"
            f"        String {v} = null;\n"
            f"        if ({v2} > {n}) {{\n"
            f"            {v} = \"active\";\n"
            f"        }}\n"
            f"        System.out.println({v}.{sm});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v2}) {{\n"
            f"{cmt}"
            f"        String {v} = null;\n"
            f"        if ({v2} > {n}) {{\n"
            f"            {v} = \"active\";\n"
            f"        }}\n"
            f"        if ({v} != null) {{\n"
            f"            System.out.println({v}.{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 8 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"'{v}' stays null when {v2} <= {n}; used outside the branch without a null check."))

    # Shape 10 — for-loop iterates uninitialized array, each element dereferenced
    for _ in range(10):
        v, m, cls, sm, n = _v(), _m(), _c(), _str_sm(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String[] {v} = new String[{n}];\n"
            f"        for (int i = 0; i < {v}.length; i++) {{\n"
            f"            System.out.println({v}[i].{sm});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String[] {v} = new String[{n}];\n"
            f"        for (int i = 0; i < {v}.length; i++) {{\n"
            f"            if ({v}[i] != null) {{\n"
            f"                System.out.println({v}[i].{sm});\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "null_pointer", ln,
            f"Array '{v}' elements are null by default; loop dereferences them without a null check."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: missing_semicolon  (10 shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_missing_semicolon() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — int variable declaration missing semicolon
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n}\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after 'int {v} = {n}'."))

    # Shape 2 — String variable declaration missing semicolon
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String {v} = \"hello\"\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String {v} = \"hello\";\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after String declaration of '{v}'."))

    # Shape 3 — void method call statement missing semicolon
    for _ in range(10):
        v, m, m2, cls = _v(), _m(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    private void {m2}(String s) {{ System.out.println(s); }}\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        {m2}(\"{v}\")\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    private void {m2}(String s) {{ System.out.println(s); }}\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        {m2}(\"{v}\");\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after method call '{m2}(\"{v}\")'."))

    # Shape 4 — return statement missing semicolon
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public int {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        return {v}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public int {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        return {v};\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after 'return {v}'."))

    # Shape 5 — assignment statement missing semicolon
    for _ in range(10):
        v, m, cls, n, n2 = _v(), _m(), _c(), _n(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        {v} = {v} + {n2}\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        {v} = {v} + {n2};\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after assignment '{v} = {v} + {n2}'."))

    # Shape 6 — boolean variable declaration missing semicolon
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(int x) {{\n"
            f"{cmt}"
            f"        boolean {v} = x > {n}\n"
            f"        if ({v}) System.out.println(\"yes\");\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(int x) {{\n"
            f"{cmt}"
            f"        boolean {v} = x > {n};\n"
            f"        if ({v}) System.out.println(\"yes\");\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after boolean declaration 'boolean {v} = x > {n}'."))

    # Shape 7 — System.out.println call missing semicolon
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        System.out.println({v})\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            "Missing semicolon after System.out.println()."))

    # Shape 8 — pre-increment statement missing semicolon
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        {v}++\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        {v}++;\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after '{v}++'."))

    # Shape 9 — object construction assignment missing semicolon
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"import java.util.ArrayList;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        java.util.List<String> {v} = new ArrayList<>()\n"
            f"        {v}.add(\"item\");\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.util.ArrayList;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        java.util.List<String> {v} = new ArrayList<>();\n"
            f"        {v}.add(\"item\");\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "missing_semicolon", ln,
            f"Missing semicolon after 'new ArrayList<>()' assignment to '{v}'."))

    # Shape 10 — static field declaration in class missing semicolon
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    private static final int {v.upper()} = {n}\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        System.out.println({v.upper()});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    private static final int {v.upper()} = {n};\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        System.out.println({v.upper()});\n"
            f"    }}\n"
            f"}}"
        )
        samples.append(_make(buggy, fixed, "missing_semicolon", 2,
            f"Missing semicolon after static field declaration '{v.upper()} = {n}'."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: unclosed_brace  (10 shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_unclosed_brace() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — instance method body missing closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        System.out.println({v});\n"
            f"    // missing closing brace for {m}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        samples.append(_make(buggy, fixed, "unclosed_brace", 2,
            f"Method '{m}' body is missing its closing brace."))

    # Shape 2 — if block missing closing brace
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v2}) {{\n"
            f"{cmt}"
            f"        if ({v2} > {n}) {{\n"
            f"            System.out.println(\"yes\");\n"
            f"        // missing closing brace for if\n"
            f"        System.out.println(\"done\");\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v2}) {{\n"
            f"{cmt}"
            f"        if ({v2} > {n}) {{\n"
            f"            System.out.println(\"yes\");\n"
            f"        }}\n"
            f"        System.out.println(\"done\");\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "unclosed_brace", ln,
            f"if block missing closing brace; subsequent statement swallowed into the block."))

    # Shape 3 — for loop body missing closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        for (int i = 0; i < {n}; i++) {{\n"
            f"            System.out.println(i);\n"
            f"        // missing closing brace for for\n"
            f"        System.out.println(\"end\");\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        for (int i = 0; i < {n}; i++) {{\n"
            f"            System.out.println(i);\n"
            f"        }}\n"
            f"        System.out.println(\"end\");\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "unclosed_brace", ln,
            f"for loop missing closing brace."))

    # Shape 4 — while loop body missing closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            {v}++;\n"
            f"        // missing closing brace for while\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            {v}++;\n"
            f"        }}\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "unclosed_brace", ln,
            f"while loop missing closing brace."))

    # Shape 5 — class body missing its final closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    private int {v} = {n};\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"// missing closing brace for class"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    private int {v} = {n};\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        samples.append(_make(buggy, fixed, "unclosed_brace", 1,
            f"Class '{cls}' is missing its final closing brace."))

    # Shape 6 — try block missing closing brace
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        try {{\n"
            f"            int {v} = Integer.parseInt(\"42\");\n"
            f"            System.out.println({v});\n"
            f"        // missing closing brace for try\n"
            f"        catch (NumberFormatException e) {{\n"
            f"            e.printStackTrace();\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        try {{\n"
            f"            int {v} = Integer.parseInt(\"42\");\n"
            f"            System.out.println({v});\n"
            f"        }} catch (NumberFormatException e) {{\n"
            f"            e.printStackTrace();\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "unclosed_brace", ln,
            f"try block missing closing brace before catch."))

    # Shape 7 — else block missing closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v}) {{\n"
            f"{cmt}"
            f"        if ({v} > {n}) {{\n"
            f"            System.out.println(\"big\");\n"
            f"        }} else {{\n"
            f"            System.out.println(\"small\");\n"
            f"        // missing closing brace for else\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v}) {{\n"
            f"{cmt}"
            f"        if ({v} > {n}) {{\n"
            f"            System.out.println(\"big\");\n"
            f"        }} else {{\n"
            f"            System.out.println(\"small\");\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "unclosed_brace", ln,
            f"else block missing closing brace."))

    # Shape 8 — static method missing closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public static int {m}(int {v}) {{\n"
            f"{cmt}"
            f"        return {v} * {n};\n"
            f"    // missing closing brace for {m}\n"
            f"\n"
            f"    public static void main(String[] args) {{\n"
            f"        System.out.println({m}(5));\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public static int {m}(int {v}) {{\n"
            f"{cmt}"
            f"        return {v} * {n};\n"
            f"    }}\n"
            f"\n"
            f"    public static void main(String[] args) {{\n"
            f"        System.out.println({m}(5));\n"
            f"    }}\n"
            f"}}"
        )
        samples.append(_make(buggy, fixed, "unclosed_brace", 2,
            f"Static method '{m}' missing its closing brace."))

    # Shape 9 — constructor missing closing brace
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    private int {v};\n"
            f"\n"
            f"    public {cls}(int {v}) {{\n"
            f"{cmt}"
            f"        this.{v} = {v};\n"
            f"    // missing closing brace for constructor\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"        System.out.println(this.{v});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    private int {v};\n"
            f"\n"
            f"    public {cls}(int {v}) {{\n"
            f"{cmt}"
            f"        this.{v} = {v};\n"
            f"    }}\n"
            f"\n"
            f"    public void {m}() {{\n"
            f"        System.out.println(this.{v});\n"
            f"    }}\n"
            f"}}"
        )
        samples.append(_make(buggy, fixed, "unclosed_brace", 4,
            f"Constructor '{cls}' missing its closing brace."))

    # Shape 10 — nested if missing inner closing brace
    for _ in range(10):
        v, v2, m, cls, n, n2 = _v(), _v(), _m(), _c(), _n(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v}, int {v2}) {{\n"
            f"{cmt}"
            f"        if ({v} > {n}) {{\n"
            f"            if ({v2} > {n2}) {{\n"
            f"                System.out.println(\"both\");\n"
            f"            // missing closing brace for inner if\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v}, int {v2}) {{\n"
            f"{cmt}"
            f"        if ({v} > {n}) {{\n"
            f"            if ({v2} > {n2}) {{\n"
            f"                System.out.println(\"both\");\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "unclosed_brace", ln,
            f"Inner if block missing its closing brace."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: array_out_of_bounds  (10 shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_array_out_of_bounds() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — arr[arr.length] instead of arr[arr.length - 1]
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        System.out.println({v}[{v}.length]);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        System.out.println({v}[{v}.length - 1]);\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Index {v}.length is one past the end; use {v}.length - 1 for the last element."))

    # Shape 2 — for loop uses <= instead of <
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        for (int i = 0; i <= {v}.length; i++) {{\n"
            f"            System.out.println({v}[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        for (int i = 0; i < {v}.length; i++) {{\n"
            f"            System.out.println({v}[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Loop condition 'i <= {v}.length' accesses index {v}.length, which is out of bounds."))

    # Shape 3 — hard-coded index equals array size (off by one)
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String[] {v} = new String[{n}];\n"
            f"        for (int i = 0; i < {n}; i++) {{\n"
            f"            {v}[i] = \"item\" + i;\n"
            f"        }}\n"
            f"        System.out.println({v}[{n}]);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        String[] {v} = new String[{n}];\n"
            f"        for (int i = 0; i < {n}; i++) {{\n"
            f"            {v}[i] = \"item\" + i;\n"
            f"        }}\n"
            f"        System.out.println({v}[{n} - 1]);\n"
            f"    }}\n"
            f"}}"
        )
        ln = 7 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Index {n} equals the array size; valid indices are 0 to {n - 1}."))

    # Shape 4 — negative index used (e.g. arr[-1])
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        int {v2} = {v}[-1];\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        int {v2} = {v}[0];\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Negative index -1 is not a valid array index."))

    # Shape 5 — 2D array, inner dimension accessed out of bounds
    for _ in range(10):
        v, m, cls, r, c = _v(), _m(), _c(), _n(2, 6), _n(2, 6)
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[][] {v} = new int[{r}][{c}];\n"
            f"        System.out.println({v}[{r - 1}][{c}]);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[][] {v} = new int[{r}][{c}];\n"
            f"        System.out.println({v}[{r - 1}][{c - 1}]);\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Column index {c} equals column size; valid range is 0 to {c - 1}."))

    # Shape 6 — ArrayList.get() with index equal to size
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"import java.util.ArrayList;\n"
            f"import java.util.List;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        List<String> {v} = new ArrayList<>();\n"
            f"        for (int i = 0; i < {n}; i++) {v}.add(\"x\" + i);\n"
            f"{cmt}"
            f"        String {v2} = {v}.get({v}.size());\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.util.ArrayList;\n"
            f"import java.util.List;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        List<String> {v} = new ArrayList<>();\n"
            f"        for (int i = 0; i < {n}; i++) {v}.add(\"x\" + i);\n"
            f"{cmt}"
            f"        String {v2} = {v}.get({v}.size() - 1);\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 9 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"List.get(size()) is one past the last element; use get(size() - 1)."))

    # Shape 7 — String.charAt() with index equal to string length
    for _ in range(10):
        v, v2, m, cls = _v(), _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(String {v}) {{\n"
            f"{cmt}"
            f"        char {v2} = {v}.charAt({v}.length());\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(String {v}) {{\n"
            f"{cmt}"
            f"        if (!{v}.isEmpty()) {{\n"
            f"            char {v2} = {v}.charAt({v}.length() - 1);\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"charAt(length()) is out of bounds; last valid index is length() - 1."))

    # Shape 8 — copying array; source index starts too high
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n(4, 12)
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        int[] {v2} = new int[{n}];\n"
            f"        for (int i = 1; i <= {n}; i++) {{\n"
            f"            {v2}[i - 1] = {v}[i];\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        int[] {v2} = new int[{n}];\n"
            f"        for (int i = 1; i < {n}; i++) {{\n"
            f"            {v2}[i - 1] = {v}[i];\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Loop bound 'i <= {n}' causes {v}[{n}] to be accessed, which is out of bounds."))

    # Shape 9 — accessing last element in loop with wrong index arithmetic
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = {{1, 2, 3, 4, 5}};\n"
            f"        int last = {n};\n"
            f"        System.out.println({v}[last]);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = {{1, 2, 3, 4, 5}};\n"
            f"        int last = {v}.length - 1;\n"
            f"        System.out.println({v}[last]);\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Hard-coded index {n} may exceed the array bounds; use {v}.length - 1."))

    # Shape 10 — reversed loop, starts at size and decrements to -1
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        for (int i = {v}.length; i >= 0; i--) {{\n"
            f"            System.out.println({v}[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int[] {v} = new int[{n}];\n"
            f"        for (int i = {v}.length - 1; i >= 0; i--) {{\n"
            f"            System.out.println({v}[i]);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "array_out_of_bounds", ln,
            f"Reverse loop starts at {v}.length; first access {v}[{v}.length] is out of bounds."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: wrong_return_type  (10 shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_wrong_return_type() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — int method returns String literal
    for _ in range(10):
        m, cls = _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public int {m}() {{\n"
            f"{cmt}"
            f"        return \"error\";\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public int {m}() {{\n"
            f"{cmt}"
            f"        return -1;\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared int but returns a String literal."))

    # Shape 2 — int method returns a boolean expression
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public int {m}(int {v}) {{\n"
            f"{cmt}"
            f"        return {v} > {n};\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public int {m}(int {v}) {{\n"
            f"{cmt}"
            f"        return {v} > {n} ? 1 : 0;\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared int but returns a boolean expression."))

    # Shape 3 — String method returns an int literal
    for _ in range(10):
        m, cls, n = _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public String {m}() {{\n"
            f"{cmt}"
            f"        return {n};\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public String {m}() {{\n"
            f"{cmt}"
            f"        return String.valueOf({n});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared String but returns an int literal."))

    # Shape 4 — boolean method returns a String literal
    for _ in range(10):
        m, cls = _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public boolean {m}() {{\n"
            f"{cmt}"
            f"        return \"true\";\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public boolean {m}() {{\n"
            f"{cmt}"
            f"        return true;\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared boolean but returns a String literal \"true\"."))

    # Shape 5 — double method returns a String literal
    for _ in range(10):
        m, cls = _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public double {m}() {{\n"
            f"{cmt}"
            f"        return \"3.14\";\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public double {m}() {{\n"
            f"{cmt}"
            f"        return 3.14;\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared double but returns a String literal."))

    # Shape 6 — int method returns a String variable
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public int {m}() {{\n"
            f"{cmt}"
            f"        String {v} = \"42\";\n"
            f"        return {v};\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public int {m}() {{\n"
            f"{cmt}"
            f"        String {v} = \"42\";\n"
            f"        return Integer.parseInt({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared int but returns String variable '{v}'."))

    # Shape 7 — String method returns an int variable
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public String {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        return {v};\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public String {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        return String.valueOf({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared String but returns int variable '{v}'."))

    # Shape 8 — boolean method returns an int literal
    for _ in range(10):
        m, cls = _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public boolean {m}(int x) {{\n"
            f"{cmt}"
            f"        return 1;\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public boolean {m}(int x) {{\n"
            f"{cmt}"
            f"        return x > 0;\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared boolean but returns int literal 1."))

    # Shape 9 — long method returns a String
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public long {m}() {{\n"
            f"{cmt}"
            f"        String {v} = \"12345\";\n"
            f"        return {v};\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public long {m}() {{\n"
            f"{cmt}"
            f"        String {v} = \"12345\";\n"
            f"        return Long.parseLong({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Method '{m}' declared long but returns String variable '{v}'."))

    # Shape 10 — void method body has a return with a value
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        return {v};\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = {n};\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "wrong_return_type", ln,
            f"Void method '{m}' incorrectly returns a value."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: infinite_loop  (10 shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_infinite_loop() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — while(true) with no break
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        while (true) {{\n"
            f"            System.out.println(\"{v}\");\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int limit = 100;\n"
            f"        int count = 0;\n"
            f"        while (count < limit) {{\n"
            f"            System.out.println(\"{v}\");\n"
            f"            count++;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"while(true) has no break or exit condition; loop runs forever."))

    # Shape 2 — for(;;) with no break
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        for (;;) {{\n"
            f"            System.out.println(\"{v}\");\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        for (int i = 0; i < 100; i++) {{\n"
            f"            System.out.println(\"{v}\");\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"for(;;) has no termination expression; loop runs forever."))

    # Shape 3 — while loop counter is never incremented
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            // {v}++ forgotten\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            {v}++;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"Loop variable '{v}' is never incremented; condition '{v} < {n}' never becomes false."))

    # Shape 4 — counter decremented instead of incremented (wrong direction)
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            {v}--;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            {v}++;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"'{v}--' decrements the counter; with '{v} < {n}' the condition never becomes false."))

    # Shape 5 — do-while(true) no break
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        do {{\n"
            f"            System.out.println(\"{v}\");\n"
            f"        }} while (true);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int count = 0;\n"
            f"        do {{\n"
            f"            System.out.println(\"{v}\");\n"
            f"            count++;\n"
            f"        }} while (count < 100);\n"
            f"    }}\n"
            f"}}"
        )
        ln = 4 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"do-while(true) has no break or counter; loop runs forever."))

    # Shape 6 — loop condition checks the wrong variable
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        int {v2} = 0;\n"
            f"        while ({v2} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            {v}++;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        int {v2} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            {v}++;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"Condition checks '{v2}' which is never modified; '{v}' is incremented but not checked."))

    # Shape 7 — break statement inside dead-code branch only
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while (true) {{\n"
            f"            {v}++;\n"
            f"            if (false) {{\n"
            f"                break;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while (true) {{\n"
            f"            {v}++;\n"
            f"            if ({v} >= {n}) {{\n"
            f"                break;\n"
            f"            }}\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"break is inside an 'if(false)' branch that never executes; loop runs forever."))

    # Shape 8 — condition reassigned to true inside loop
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        boolean {v} = true;\n"
            f"        int {v2} = 0;\n"
            f"        while ({v}) {{\n"
            f"            {v2}++;\n"
            f"            {v} = true;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        boolean {v} = true;\n"
            f"        int {v2} = 0;\n"
            f"        while ({v}) {{\n"
            f"            {v2}++;\n"
            f"            if ({v2} >= {n}) {v} = false;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 7 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"Flag '{v}' is reset to true inside the loop; the exit condition is never reached."))

    # Shape 9 — for loop update expression goes wrong direction
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        for (int {v} = 0; {v} < {n}; {v}--) {{\n"
            f"            System.out.println({v});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"{cmt}"
            f"        for (int {v} = 0; {v} < {n}; {v}++) {{\n"
            f"            System.out.println({v});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 3 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"for loop decrements '{v}' but condition '{v} < {n}' requires an increment."))

    # Shape 10 — while loop counter incremented in wrong branch only
    for _ in range(10):
        v, v2, m, cls, n, n2 = _v(), _v(), _m(), _c(), _n(), _n()
        cmt = _cmt()
        buggy = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v2}) {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            if ({v2} > {n2}) {{\n"
            f"                {v}++;\n"
            f"            }}\n"
            f"            System.out.println({v});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"public class {cls} {{\n"
            f"    public void {m}(int {v2}) {{\n"
            f"{cmt}"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            if ({v2} > {n2}) {{\n"
            f"                {v}++;\n"
            f"            }} else {{\n"
            f"                {v}++;\n"
            f"            }}\n"
            f"            System.out.println({v});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "infinite_loop", ln,
            f"'{v}' incremented only when {v2} > {n2}; if that condition never holds the loop is infinite."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Bug generator: resource_leak  (10 shapes × 10 variants = 100)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_resource_leak() -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []

    # Shape 1 — FileReader opened, never closed
    for _ in range(10):
        v, m, cls, fp = _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.FileReader;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        FileReader {v} = new FileReader({fp});\n"
            f"        int ch = {v}.read();\n"
            f"        System.out.println(ch);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.FileReader;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (FileReader {v} = new FileReader({fp})) {{\n"
            f"            int ch = {v}.read();\n"
            f"            System.out.println(ch);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"FileReader '{v}' is opened but never closed; use try-with-resources."))

    # Shape 2 — BufferedReader opened, never closed
    for _ in range(10):
        v, v2, m, cls, fp = _v(), _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        BufferedReader {v} = new BufferedReader(new FileReader({fp}));\n"
            f"        String {v2} = {v}.readLine();\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (BufferedReader {v} = new BufferedReader(new FileReader({fp}))) {{\n"
            f"            String {v2} = {v}.readLine();\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"BufferedReader '{v}' is never closed; wrap in try-with-resources."))

    # Shape 3 — FileWriter opened, never closed
    for _ in range(10):
        v, m, cls, fp = _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.FileWriter;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        FileWriter {v} = new FileWriter({fp});\n"
            f"        {v}.write(\"data\");\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.FileWriter;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (FileWriter {v} = new FileWriter({fp})) {{\n"
            f"            {v}.write(\"data\");\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"FileWriter '{v}' is never closed; buffered data may not be flushed."))

    # Shape 4 — Scanner(File) opened, never closed
    for _ in range(10):
        v, v2, m, cls, fp = _v(), _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.File;\n"
            f"import java.util.Scanner;\n"
            f"import java.io.FileNotFoundException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws FileNotFoundException {{\n"
            f"{cmt}"
            f"        Scanner {v} = new Scanner(new File({fp}));\n"
            f"        String {v2} = {v}.nextLine();\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.File;\n"
            f"import java.util.Scanner;\n"
            f"import java.io.FileNotFoundException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws FileNotFoundException {{\n"
            f"{cmt}"
            f"        try (Scanner {v} = new Scanner(new File({fp}))) {{\n"
            f"            String {v2} = {v}.nextLine();\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 7 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"Scanner '{v}' is never closed; use try-with-resources."))

    # Shape 5 — FileInputStream opened, never closed
    for _ in range(10):
        v, m, cls, fp = _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.FileInputStream;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        FileInputStream {v} = new FileInputStream({fp});\n"
            f"        int b = {v}.read();\n"
            f"        System.out.println(b);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.FileInputStream;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (FileInputStream {v} = new FileInputStream({fp})) {{\n"
            f"            int b = {v}.read();\n"
            f"            System.out.println(b);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"FileInputStream '{v}' is never closed; OS file descriptor is leaked."))

    # Shape 6 — FileOutputStream opened, never closed
    for _ in range(10):
        v, m, cls, fp = _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.FileOutputStream;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        FileOutputStream {v} = new FileOutputStream({fp});\n"
            f"        {v}.write(42);\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.FileOutputStream;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (FileOutputStream {v} = new FileOutputStream({fp})) {{\n"
            f"            {v}.write(42);\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"FileOutputStream '{v}' is never closed; unflushed bytes may be lost."))

    # Shape 7 — PrintWriter(File) opened, never closed
    for _ in range(10):
        v, m, cls, fp = _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.PrintWriter;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        PrintWriter {v} = new PrintWriter({fp});\n"
            f"        {v}.println(\"output\");\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.PrintWriter;\n"
            f"import java.io.IOException;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (PrintWriter {v} = new PrintWriter({fp})) {{\n"
            f"            {v}.println(\"output\");\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 6 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"PrintWriter '{v}' is never closed; output may not be flushed to disk."))

    # Shape 8 — InputStreamReader opened, never closed
    for _ in range(10):
        v, v2, m, cls, fp = _v(), _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        InputStreamReader {v} = new InputStreamReader(\n"
            f"            new FileInputStream({fp}));\n"
            f"        int {v2} = {v}.read();\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (InputStreamReader {v} = new InputStreamReader(\n"
            f"            new FileInputStream({fp}))) {{\n"
            f"            int {v2} = {v}.read();\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"InputStreamReader '{v}' is never closed; use try-with-resources."))

    # Shape 9 — resource opened but close() only called on happy path (not in finally)
    for _ in range(10):
        v, v2, m, cls, fp = _v(), _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        BufferedReader {v} = new BufferedReader(new FileReader({fp}));\n"
            f"        String {v2} = {v}.readLine();\n"
            f"        System.out.println({v2});\n"
            f"        {v}.close();\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (BufferedReader {v} = new BufferedReader(new FileReader({fp}))) {{\n"
            f"            String {v2} = {v}.readLine();\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"'{v}.close()' only runs on the happy path; an exception before it leaks the resource."))

    # Shape 10 — BufferedWriter opened, never closed
    for _ in range(10):
        v, m, cls, fp = _v(), _m(), _c(), _f()
        cmt = _cmt()
        buggy = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        BufferedWriter {v} = new BufferedWriter(new FileWriter({fp}));\n"
            f"        {v}.write(\"hello\");\n"
            f"        {v}.newLine();\n"
            f"    }}\n"
            f"}}"
        )
        fixed = (
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"{cmt}"
            f"        try (BufferedWriter {v} = new BufferedWriter(new FileWriter({fp}))) {{\n"
            f"            {v}.write(\"hello\");\n"
            f"            {v}.newLine();\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )
        ln = 5 + (1 if cmt else 0)
        samples.append(_make(buggy, fixed, "resource_leak", ln,
            f"BufferedWriter '{v}' is never closed; buffered content is not flushed."))

    return samples


# ─────────────────────────────────────────────────────────────────────────────
# Clean sample generators
# ─────────────────────────────────────────────────────────────────────────────

def _gen_original_clean() -> list[dict[str, Any]]:
    """100 clean Java snippets that were never derived from a bug."""
    snippets: list[str] = []

    # 10 shapes × 10 variants = 100

    # Shape A — simple addition utility method
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public int {m}(int {v}, int {v2}) {{\n"
            f"        return {v} + {v2};\n"
            f"    }}\n"
            f"}}"
        )

    # Shape B — null-safe string method
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public String {m}(String {v}) {{\n"
            f"        if ({v} == null || {v}.isEmpty()) {{\n"
            f"            return \"default\";\n"
            f"        }}\n"
            f"        return {v}.trim().toUpperCase();\n"
            f"    }}\n"
            f"}}"
        )

    # Shape C — try-with-resources reading a file
    for _ in range(10):
        v, v2, m, cls, fp = _v(), _v(), _m(), _c(), _f()
        snippets.append(
            f"import java.io.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() throws IOException {{\n"
            f"        try (BufferedReader {v} = new BufferedReader(new FileReader({fp}))) {{\n"
            f"            String {v2} = {v}.readLine();\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )

    # Shape D — safe array iteration
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        int[] {v} = new int[{n}];\n"
            f"        for (int i = 0; i < {v}.length; i++) {{\n"
            f"            {v}[i] = i * 2;\n"
            f"        }}\n"
            f"        System.out.println({v}[{n} - 1]);\n"
            f"    }}\n"
            f"}}"
        )

    # Shape E — simple class with constructor and getter
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        snippets.append(
            f"public class {cls} {{\n"
            f"    private final int {v};\n"
            f"\n"
            f"    public {cls}(int {v}) {{\n"
            f"        this.{v} = {v};\n"
            f"    }}\n"
            f"\n"
            f"    public int get{v.capitalize()}() {{\n"
            f"        return this.{v};\n"
            f"    }}\n"
            f"}}"
        )

    # Shape F — HashMap usage with null-safe get
    for _ in range(10):
        v, v2, m, cls = _v(), _v(), _m(), _c()
        snippets.append(
            f"import java.util.HashMap;\n"
            f"import java.util.Map;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        Map<String, String> {v} = new HashMap<>();\n"
            f"        {v}.put(\"key\", \"value\");\n"
            f"        String {v2} = {v}.getOrDefault(\"key\", \"missing\");\n"
            f"        System.out.println({v2});\n"
            f"    }}\n"
            f"}}"
        )

    # Shape G — bounded while loop
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        int {v} = 0;\n"
            f"        while ({v} < {n}) {{\n"
            f"            System.out.println({v});\n"
            f"            {v}++;\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )

    # Shape H — static utility with correct return type
    for _ in range(10):
        v, m, cls, n = _v(), _m(), _c(), _n()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public static boolean {m}(int {v}) {{\n"
            f"        return {v} > 0 && {v} < {n};\n"
            f"    }}\n"
            f"\n"
            f"    public static void main(String[] args) {{\n"
            f"        System.out.println({m}(5));\n"
            f"    }}\n"
            f"}}"
        )

    # Shape I — proper try/catch block
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public void {m}(String {v}) {{\n"
            f"        try {{\n"
            f"            int result = Integer.parseInt({v});\n"
            f"            System.out.println(result);\n"
            f"        }} catch (NumberFormatException e) {{\n"
            f"            System.err.println(\"Invalid number: \" + {v});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )

    # Shape J — ArrayList with bounds-safe access
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        snippets.append(
            f"import java.util.ArrayList;\n"
            f"import java.util.List;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        List<Integer> {v} = new ArrayList<>();\n"
            f"        for (int i = 0; i < {n}; i++) {v}.add(i);\n"
            f"        if (!{v}.isEmpty()) {{\n"
            f"            int {v2} = {v}.get({v}.size() - 1);\n"
            f"            System.out.println({v2});\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )

    return [_clean(s) for s in snippets]


def _gen_extra_clean() -> list[dict[str, Any]]:
    """100 additional varied clean snippets to strengthen clean-class balance."""
    snippets: list[str] = []

    # 10 shapes × 10 variants = 100

    # Shape AA — String switch statement
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public String {m}(String {v}) {{\n"
            f"        switch ({v}) {{\n"
            f"            case \"a\": return \"alpha\";\n"
            f"            case \"b\": return \"beta\";\n"
            f"            default:  return \"unknown\";\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )

    # Shape BB — recursive factorial (with base case)
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public long {m}(int {v}) {{\n"
            f"        if ({v} <= 1) return 1L;\n"
            f"        return {v} * {m}({v} - 1);\n"
            f"    }}\n"
            f"}}"
        )

    # Shape CC — interface implementation stub
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls} implements Runnable {{\n"
            f"    private final String {v};\n"
            f"\n"
            f"    public {cls}(String {v}) {{\n"
            f"        this.{v} = {v};\n"
            f"    }}\n"
            f"\n"
            f"    @Override\n"
            f"    public void run() {{\n"
            f"        System.out.println({v});\n"
            f"    }}\n"
            f"}}"
        )

    # Shape DD — for-each over list
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        snippets.append(
            f"import java.util.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}() {{\n"
            f"        List<String> {v} = Arrays.asList(\"x\", \"y\", \"z\");\n"
            f"        for (String {v2} : {v}) {{\n"
            f"            System.out.println({v2}.toUpperCase());\n"
            f"        }}\n"
            f"    }}\n"
            f"}}"
        )

    # Shape EE — Optional usage
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"import java.util.Optional;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}(Optional<String> {v}) {{\n"
            f"        String result = {v}.orElse(\"default\");\n"
            f"        System.out.println(result.toUpperCase());\n"
            f"    }}\n"
            f"}}"
        )

    # Shape FF — StringBuilder usage
    for _ in range(10):
        v, v2, m, cls, n = _v(), _v(), _m(), _c(), _n()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public String {m}(int {v2}) {{\n"
            f"        StringBuilder {v} = new StringBuilder();\n"
            f"        for (int i = 0; i < {v2}; i++) {{\n"
            f"            {v}.append(i).append(\",\");\n"
            f"        }}\n"
            f"        return {v}.toString();\n"
            f"    }}\n"
            f"}}"
        )

    # Shape GG — enum with method
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls} {{\n"
            f"    enum Status {{ ACTIVE, INACTIVE, PENDING }}\n"
            f"\n"
            f"    public boolean {m}(Status {v}) {{\n"
            f"        return {v} == Status.ACTIVE;\n"
            f"    }}\n"
            f"}}"
        )

    # Shape HH — Collections.sort with Comparator
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"import java.util.*;\n"
            f"\n"
            f"public class {cls} {{\n"
            f"    public void {m}(List<String> {v}) {{\n"
            f"        Collections.sort({v}, Comparator.naturalOrder());\n"
            f"        for (String s : {v}) System.out.println(s);\n"
            f"    }}\n"
            f"}}"
        )

    # Shape II — Math utility
    for _ in range(10):
        v, v2, m, cls = _v(), _v(), _m(), _c()
        snippets.append(
            f"public class {cls} {{\n"
            f"    public double {m}(double {v}, double {v2}) {{\n"
            f"        if ({v2} == 0.0) throw new ArithmeticException(\"divisor is zero\");\n"
            f"        return {v} / {v2};\n"
            f"    }}\n"
            f"}}"
        )

    # Shape JJ — generic class
    for _ in range(10):
        v, m, cls = _v(), _m(), _c()
        snippets.append(
            f"public class {cls}<T> {{\n"
            f"    private T {v};\n"
            f"\n"
            f"    public void set{v.capitalize()}(T {v}) {{\n"
            f"        this.{v} = {v};\n"
            f"    }}\n"
            f"\n"
            f"    public T get{v.capitalize()}() {{\n"
            f"        return this.{v};\n"
            f"    }}\n"
            f"}}"
        )

    return [_clean(s) for s in snippets]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_java_samples() -> list[dict[str, Any]]:
    """
    Generate all Java training rows.

    Returns a list of dicts, each with keys:
      code, language, is_bug, bug_type, line_number, description, fixed_code
    """
    buggy_generators = [
        ("null_pointer",        _gen_null_pointer),
        ("missing_semicolon",   _gen_missing_semicolon),
        ("unclosed_brace",      _gen_unclosed_brace),
        ("array_out_of_bounds", _gen_array_out_of_bounds),
        ("wrong_return_type",   _gen_wrong_return_type),
        ("infinite_loop",       _gen_infinite_loop),
        ("resource_leak",       _gen_resource_leak),
    ]

    all_rows: list[dict[str, Any]] = []

    for bug_type, gen_fn in buggy_generators:
        buggy_samples = gen_fn()
        assert len(buggy_samples) == 100, (
            f"Expected 100 buggy samples for {bug_type}, got {len(buggy_samples)}"
        )
        all_rows.extend(buggy_samples)
        all_rows.extend(_to_clean(s) for s in buggy_samples)

    all_rows.extend(_gen_original_clean())
    all_rows.extend(_gen_extra_clean())

    return all_rows


def save_to_csv(samples: list[dict[str, Any]], path: str) -> None:
    """Write samples to a CSV file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    fieldnames = ["code", "language", "is_bug", "bug_type", "line_number",
                  "description", "fixed_code"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(samples)


# ─────────────────────────────────────────────────────────────────────────────
# Cross-language row factories
# ─────────────────────────────────────────────────────────────────────────────

def _make_lang(
    lang: str,
    code: str,
    fixed: str,
    bug_type: str,
    line_number: int,
    description: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "language": lang,
        "is_bug": 1,
        "bug_type": bug_type,
        "line_number": line_number,
        "description": description,
        "fixed_code": fixed,
    }


def _clean_lang(code: str, lang: str) -> dict[str, Any]:
    return {
        "code": code,
        "language": lang,
        "is_bug": 0,
        "bug_type": "clean",
        "line_number": 0,
        "description": "No bugs found.",
        "fixed_code": code,
    }


# Pool of names for the "undeclared" variable in C undeclared_variable shapes
_UD_NAMES: list[str] = [
    "count", "total", "result", "answer", "flag", "idx",
    "baseline", "offset", "limit", "accumulator", "score",
    "threshold", "tracker", "avg_val", "max_val",
]


def _ud() -> str:
    return random.choice(_UD_NAMES)


# ─────────────────────────────────────────────────────────────────────────────
# C — bug generators (10 shapes × 10 variants = 100 per bug type)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_c_missing_semicolon() -> list[dict[str, Any]]:
    s, L = [], "c"

    # Shape 1: int variable declaration missing ;
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int {v2} = {n}\n"
                 f"    printf(\"%d\\n\", {v2});\n    return {v2};\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int {v2} = {n};\n"
                 f"    printf(\"%d\\n\", {v2});\n    return {v2};\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            f"Missing semicolon after 'int {v2} = {n}'."))

    # Shape 2: printf statement missing ;
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}(int {v}) {{\n"
                 f"    printf(\"%d\\n\", {v})\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}(int {v}) {{\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            "Missing semicolon after printf() call."))

    # Shape 3: return statement missing ;
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int {v2} = {v} + {n};\n    return {v2}\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int {v2} = {v} + {n};\n    return {v2};\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after 'return {v2}'."))

    # Shape 4: assignment statement missing ;
    for _ in range(10):
        v, fn, n, n2 = _v(), _m(), _n(), _n()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v} = {v} * {n2}\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v} = {v} * {n2};\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after '{v} = {v} * {n2}'."))

    # Shape 5: float declaration missing ;
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    float {v} = 3.14\n    printf(\"%.2f\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    float {v} = 3.14;\n    printf(\"%.2f\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            f"Missing semicolon after 'float {v} = 3.14'."))

    # Shape 6: char declaration missing ;
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v} = 'A'\n    printf(\"%c\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v} = 'A';\n    printf(\"%c\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            f"Missing semicolon after 'char {v} = \\'A\\''."))

    # Shape 7: post-increment missing ;
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v}++\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v}++;\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after '{v}++'."))

    # Shape 8: scanf call missing ;
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v};\n    scanf(\"%d\", &{v})\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v};\n    scanf(\"%d\", &{v});\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            "Missing semicolon after scanf() call."))

    # Shape 9: double declaration missing ;
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    double {v} = 2.718\n    int {v2} = (int){v};\n"
                 f"    printf(\"%d\\n\", {v2});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    double {v} = 2.718;\n    int {v2} = (int){v};\n"
                 f"    printf(\"%d\\n\", {v2});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            f"Missing semicolon after 'double {v} = 2.718'."))

    # Shape 10: pointer declaration missing ;
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    int *{v2} = &{v}\n"
                 f"    printf(\"%d\\n\", *{v2});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    int *{v2} = &{v};\n"
                 f"    printf(\"%d\\n\", *{v2});\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after 'int *{v2} = &{v}'."))
    return s


def _gen_c_undeclared_variable() -> list[dict[str, Any]]:
    s, L = [], "c"

    # Shape 1: undeclared variable printed directly
    for _ in range(10):
        fn, ud = _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    printf(\"%d\\n\", {ud});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {ud} = 0;\n    printf(\"%d\\n\", {ud});\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"Variable '{ud}' used but never declared."))

    # Shape 2: undeclared variable in arithmetic
    for _ in range(10):
        v, fn, ud = _v(), _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int result = {v} + {ud};\n    return result;\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int {ud} = 0;\n    int result = {v} + {ud};\n"
                 f"    return result;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"'{ud}' used in arithmetic but never declared."))

    # Shape 3: undeclared variable in condition
    for _ in range(10):
        fn, n, ud = _m(), _n(), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    if ({ud} > {n}) {{\n        printf(\"yes\\n\");\n    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {ud} = 0;\n    if ({ud} > {n}) {{\n"
                 f"        printf(\"yes\\n\");\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"'{ud}' used in condition but never declared."))

    # Shape 4: undeclared variable in return statement
    for _ in range(10):
        v, fn, ud = _v(), _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int x = {v} * 2;\n    return {ud};\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int x = {v} * 2;\n    int {ud} = x;\n    return {ud};\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 5,
                            f"'{ud}' used in return but never declared."))

    # Shape 5: undeclared variable as array subscript
    for _ in range(10):
        v, fn, n, ud = _v(), _m(), _n(5, 14), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n    {v}[{ud}] = 5;\n"
                 f"    printf(\"%d\\n\", {v}[0]);\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n    int {ud} = 0;\n"
                 f"    {v}[{ud}] = 5;\n    printf(\"%d\\n\", {v}[0]);\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 5,
                            f"Array subscript '{ud}' used but never declared."))

    # Shape 6: undeclared variable as loop limit
    for _ in range(10):
        fn, ud = _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    for (int i = 0; i < {ud}; i++) {{\n"
                 f"        printf(\"%d\\n\", i);\n    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {ud} = 10;\n"
                 f"    for (int i = 0; i < {ud}; i++) {{\n"
                 f"        printf(\"%d\\n\", i);\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"Loop limit '{ud}' used but never declared."))

    # Shape 7: undeclared variable passed as argument
    for _ in range(10):
        fn, fn2, ud = _m(), _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn2}(int x) {{\n"
                 f"    printf(\"%d\\n\", x);\n}}\n\n"
                 f"void {fn}() {{\n    {fn2}({ud});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn2}(int x) {{\n"
                 f"    printf(\"%d\\n\", x);\n}}\n\n"
                 f"void {fn}() {{\n    int {ud} = 0;\n    {fn2}({ud});\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 8,
                            f"'{ud}' passed to {fn2}() but never declared."))

    # Shape 8: undeclared pointer dereferenced
    for _ in range(10):
        v, fn, ud = _v(), _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = *{ud};\n    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int tmp = 42;\n    int *{ud} = &tmp;\n"
                 f"    int {v} = *{ud};\n    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"Pointer '{ud}' dereferenced but never declared."))

    # Shape 9: undeclared variable used in subtraction
    for _ in range(10):
        v, fn, ud = _v(), _m(), _ud()
        buggy = (f"#include <stdio.h>\n\ndouble {fn}(double {v}) {{\n"
                 f"    double diff = {v} - {ud};\n    return diff;\n}}")
        fixed = (f"#include <stdio.h>\n\ndouble {fn}(double {v}) {{\n"
                 f"    double {ud} = 0.0;\n"
                 f"    double diff = {v} - {ud};\n    return diff;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"'{ud}' used in subtraction but never declared."))

    # Shape 10: undeclared variable on RHS of assignment
    for _ in range(10):
        v, fn, ud = _v(), _m(), _ud()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {ud} + 1;\n    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {ud} = 0;\n    int {v} = {ud} + 1;\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "undeclared_variable", 4,
                            f"'{ud}' used on RHS of assignment but never declared."))
    return s


def _gen_c_buffer_overflow() -> list[dict[str, Any]]:
    s, L = [], "c"

    # Shape 1: strcpy into too-small buffer
    for _ in range(10):
        v, fn = _v(), _m()
        sz = random.choice([4, 6, 8, 10])
        buggy = (f"#include <string.h>\n#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[{sz}];\n"
                 f"    strcpy({v}, \"this string is way too long for the buffer\");\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <string.h>\n#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[{sz}];\n"
                 f"    strncpy({v}, \"short\", sizeof({v}) - 1);\n"
                 f"    {v}[sizeof({v}) - 1] = '\\0';\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 6,
                            f"strcpy writes past the {sz}-byte buffer '{v}'; use strncpy."))

    # Shape 2: for loop uses <= arr.length (off by one)
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(5, 14)
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n"
                 f"    for (int i = 0; i <= {n}; i++) {{\n"
                 f"        {v}[i] = i;\n    }}\n"
                 f"    printf(\"%d\\n\", {v}[{n}-1]);\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n"
                 f"    for (int i = 0; i < {n}; i++) {{\n"
                 f"        {v}[i] = i;\n    }}\n"
                 f"    printf(\"%d\\n\", {v}[{n}-1]);\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 5,
                            f"Loop bound 'i <= {n}' writes to {v}[{n}], which is out of bounds."))

    # Shape 3: hard-coded index equals array size
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(4, 12)
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n"
                 f"    for (int i = 0; i < {n}; i++) {v}[i] = i;\n"
                 f"    {v}[{n}] = 99;\n"
                 f"    printf(\"%d\\n\", {v}[{n}-1]);\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n"
                 f"    for (int i = 0; i < {n}; i++) {v}[i] = i;\n"
                 f"    {v}[{n}-1] = 99;\n"
                 f"    printf(\"%d\\n\", {v}[{n}-1]);\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 6,
                            f"Index {n} equals the array size; valid range is 0 to {n-1}."))

    # Shape 4: sprintf to too-small buffer
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}(int num) {{\n"
                 f"    char {v}[4];\n"
                 f"    sprintf({v}, \"%d\", num);\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}(int num) {{\n"
                 f"    char {v}[16];\n"
                 f"    snprintf({v}, sizeof({v}), \"%d\", num);\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 5,
                            f"sprintf into 4-byte '{v}' can overflow for multi-digit integers."))

    # Shape 5: strcat without size check
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <string.h>\n#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[8] = \"hi\";\n"
                 f"    strcat({v}, \"this suffix is too long\");\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <string.h>\n#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[64] = \"hi\";\n"
                 f"    strncat({v}, \"this suffix is too long\",\n"
                 f"            sizeof({v}) - strlen({v}) - 1);\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 6,
                            f"strcat writes past the 8-byte '{v}' buffer; use strncat."))

    # Shape 6: gets() — always unsafe
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[32];\n    gets({v});\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[32];\n    fgets({v}, sizeof({v}), stdin);\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 5,
                            f"gets() has no bounds check; any input overflows '{v}'."))

    # Shape 7: memcpy with source sizeof > destination sizeof
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <string.h>\n#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[8];\n"
                 f"    char {v2}[] = \"this is a very long string indeed\";\n"
                 f"    memcpy({v}, {v2}, sizeof({v2}));\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <string.h>\n#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char {v}[8];\n"
                 f"    char {v2}[] = \"this is a very long string indeed\";\n"
                 f"    memcpy({v}, {v2}, sizeof({v}) - 1);\n"
                 f"    {v}[sizeof({v}) - 1] = '\\0';\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 7,
                            f"memcpy copies sizeof({v2}) bytes into 8-byte '{v}'; overflow."))

    # Shape 8: char-by-char copy with no length guard
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}(const char *src) {{\n"
                 f"    char {v}[8];\n    int i = 0;\n"
                 f"    while (src[i] != '\\0') {{\n"
                 f"        {v}[i] = src[i];\n        i++;\n    }}\n"
                 f"    {v}[i] = '\\0';\n    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}(const char *src) {{\n"
                 f"    char {v}[8];\n    int i = 0;\n"
                 f"    while (src[i] != '\\0' && i < (int)sizeof({v}) - 1) {{\n"
                 f"        {v}[i] = src[i];\n        i++;\n    }}\n"
                 f"    {v}[i] = '\\0';\n    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 6,
                            f"Copy loop lacks a bounds check on '{v}'; long inputs overflow."))

    # Shape 9: reverse loop starts at array size (off by one)
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(5, 14)
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n"
                 f"    for (int i = {n}; i >= 0; i--) {{\n"
                 f"        {v}[i] = i;\n    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v}[{n}];\n"
                 f"    for (int i = {n}-1; i >= 0; i--) {{\n"
                 f"        {v}[i] = i;\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 5,
                            f"Reverse loop starts at {n}; first access {v}[{n}] is out of bounds."))

    # Shape 10: snprintf with too-small size argument
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}(const char *name) {{\n"
                 f"    char {v}[64];\n"
                 f"    snprintf({v}, 4, \"Hello, %s!\", name);\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}(const char *name) {{\n"
                 f"    char {v}[64];\n"
                 f"    snprintf({v}, sizeof({v}), \"Hello, %s!\", name);\n"
                 f"    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "buffer_overflow", 5,
                            f"snprintf size argument is 4 but '{v}' is 64 bytes; use sizeof({v})."))
    return s


def _gen_c_missing_return() -> list[dict[str, Any]]:
    s, L = [], "c"

    # Shape 1: int function with only printf
    for _ in range(10):
        fn = _m()
        buggy = (f"#include <stdio.h>\n\nint {fn}() {{\n"
                 f"    printf(\"hello\\n\");\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}() {{\n"
                 f"    printf(\"hello\\n\");\n    return 0;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 5,
                            f"Non-void function '{fn}' has no return statement."))

    # Shape 2: int function with conditional return only on one branch
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    if ({v} > {n}) {{\n        return 1;\n    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    if ({v} > {n}) {{\n        return 1;\n    }}\n"
                 f"    return 0;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"'{fn}' returns on the if-branch but has no return for the else case."))

    # Shape 3: double function, computes but doesn't return
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\ndouble {fn}(double {v}) {{\n"
                 f"    double result = {v} * 2.0;\n"
                 f"    printf(\"%.2f\\n\", result);\n}}")
        fixed = (f"#include <stdio.h>\n\ndouble {fn}(double {v}) {{\n"
                 f"    double result = {v} * 2.0;\n"
                 f"    printf(\"%.2f\\n\", result);\n    return result;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"double function '{fn}' never returns a value."))

    # Shape 4: int function — only assignments, no return
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int x = {v} * {n};\n    int y = x + 1;\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int x = {v} * {n};\n    int y = x + 1;\n    return y;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"'{fn}' computes 'y' but never returns it."))

    # Shape 5: char function, no return
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nchar {fn}(int {v}) {{\n"
                 f"    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nchar {fn}(int {v}) {{\n"
                 f"    printf(\"%d\\n\", {v});\n    return (char){v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 5,
                            f"char function '{fn}' has no return statement."))

    # Shape 6: long function with two params, no return
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <stdio.h>\n\nlong {fn}(int {v}, int {v2}) {{\n"
                 f"    int sum = {v} + {v2};\n    printf(\"%d\\n\", sum);\n}}")
        fixed = (f"#include <stdio.h>\n\nlong {fn}(int {v}, int {v2}) {{\n"
                 f"    int sum = {v} + {v2};\n    printf(\"%d\\n\", sum);\n"
                 f"    return (long)sum;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"long function '{fn}' never returns."))

    # Shape 7: int function with while loop, no return
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int i = 0;\n    while (i < {v}) {{\n"
                 f"        printf(\"%d\\n\", i);\n        i++;\n    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    int i = 0;\n    while (i < {v}) {{\n"
                 f"        printf(\"%d\\n\", i);\n        i++;\n    }}\n"
                 f"    return i;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 9,
                            f"int function '{fn}' has a while loop but no return after it."))

    # Shape 8: int function with for loop, no return
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    for (int i = 0; i < {v}; i++) {{\n"
                 f"        printf(\"%d\\n\", i);\n    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}) {{\n"
                 f"    for (int i = 0; i < {v}; i++) {{\n"
                 f"        printf(\"%d\\n\", i);\n    }}\n    return 0;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 7,
                            f"int function '{fn}' has a for loop but no return statement."))

    # Shape 9: unsigned int function, no return
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nunsigned int {fn}(int {v}) {{\n"
                 f"    int b = {v} * {n};\n    printf(\"%d\\n\", b);\n}}")
        fixed = (f"#include <stdio.h>\n\nunsigned int {fn}(int {v}) {{\n"
                 f"    int b = {v} * {n};\n    printf(\"%d\\n\", b);\n"
                 f"    return (unsigned int)b;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"unsigned int function '{fn}' never returns a value."))

    # Shape 10: nested if, outer else missing return
    for _ in range(10):
        v, v2, fn, n, n2 = _v(), _v(), _m(), _n(), _n()
        buggy = (f"#include <stdio.h>\n\nint {fn}(int {v}, int {v2}) {{\n"
                 f"    if ({v} > {n}) {{\n"
                 f"        if ({v2} > {n2}) {{\n            return 1;\n        }}\n"
                 f"    }}\n}}")
        fixed = (f"#include <stdio.h>\n\nint {fn}(int {v}, int {v2}) {{\n"
                 f"    if ({v} > {n}) {{\n"
                 f"        if ({v2} > {n2}) {{\n            return 1;\n        }}\n"
                 f"    }}\n    return 0;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 9,
                            f"'{fn}' returns 1 in the nested branch but has no return for other paths."))
    return s


def _gen_c_wrong_format_specifier() -> list[dict[str, Any]]:
    s, L = [], "c"

    # Shape 1: %d used for float
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    float {v} = 3.14f;\n    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    float {v} = 3.14f;\n    printf(\"%f\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%d used for float variable '{v}'; should be %%f."))

    # Shape 2: %d used for double
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    double {v} = 2.718;\n    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    double {v} = 2.718;\n    printf(\"%lf\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%d used for double '{v}'; should be %%lf."))

    # Shape 3: %f used for int
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    printf(\"%f\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%f used for int '{v}'; should be %%d."))

    # Shape 4: %s used for int
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    printf(\"%s\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%s used for int '{v}'; should be %%d."))

    # Shape 5: %d used for char* pointer
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char *{v} = \"hello\";\n    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    char *{v} = \"hello\";\n    printf(\"%s\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%d used for char* '{v}'; should be %%s."))

    # Shape 6: %d used for long (should be %ld)
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    long {v} = 1234567890L;\n    printf(\"%d\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    long {v} = 1234567890L;\n    printf(\"%ld\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%d used for long '{v}'; should be %%ld."))

    # Shape 7: %f used for long
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    long {v} = 9876543L;\n    printf(\"%f\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    long {v} = 9876543L;\n    printf(\"%ld\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%f used for long '{v}'; should be %%ld."))

    # Shape 8: %i used for double
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    double {v} = 3.14159;\n    printf(\"%i\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    double {v} = 3.14159;\n    printf(\"%lf\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%i used for double '{v}'; should be %%lf."))

    # Shape 9: %d for float element in array
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    float {v}[3] = {{1.0f, 2.0f, 3.0f}};\n"
                 f"    printf(\"%d\\n\", {v}[0]);\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    float {v}[3] = {{1.0f, 2.0f, 3.0f}};\n"
                 f"    printf(\"%f\\n\", {v}[0]);\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%d used for float array element {v}[0]; should be %%f."))

    # Shape 10: %lf used for int
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    printf(\"%lf\\n\", {v});\n}}")
        fixed = (f"#include <stdio.h>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    printf(\"%d\\n\", {v});\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_format_specifier", 5,
                            f"%%lf used for int '{v}'; should be %%d."))
    return s


def generate_c_samples() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gen in [_gen_c_missing_semicolon, _gen_c_undeclared_variable,
                _gen_c_buffer_overflow, _gen_c_missing_return,
                _gen_c_wrong_format_specifier]:
        buggy = gen()
        assert len(buggy) == 100, f"{gen.__name__} produced {len(buggy)} samples"
        rows.extend(buggy)
        rows.extend(_to_clean(s) for s in buggy)
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# C++ — bug generators (10 shapes × 10 variants = 100 per bug type)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_cpp_memory_leak() -> list[dict[str, Any]]:
    s, L = [], "cpp"

    # Shape 1: int* allocated with new, never deleted
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = new int({n});\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = new int({n});\n"
                 f"    std::cout << *{v} << std::endl;\n    delete {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 4,
                            f"int* '{v}' allocated with new but never deleted."))

    # Shape 2: new std::string, never deleted
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <string>\n\nvoid {fn}() {{\n"
                 f"    std::string* {v} = new std::string(\"hello\");\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <string>\n\nvoid {fn}() {{\n"
                 f"    std::string* {v} = new std::string(\"hello\");\n"
                 f"    std::cout << *{v} << std::endl;\n    delete {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 5,
                            f"std::string* '{v}' never deleted; use delete."))

    # Shape 3: new int[] (array), never deleted with delete[]
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}(int size) {{\n"
                 f"    int* {v} = new int[size];\n"
                 f"    for (int i = 0; i < size; i++) {v}[i] = i;\n"
                 f"    std::cout << {v}[0] << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int size) {{\n"
                 f"    int* {v} = new int[size];\n"
                 f"    for (int i = 0; i < size; i++) {v}[i] = i;\n"
                 f"    std::cout << {v}[0] << std::endl;\n    delete[] {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 4,
                            f"Array '{v}' allocated with new[] but never freed with delete[]."))

    # Shape 4: pointer reassigned without deleting previous allocation
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = new int(1);\n"
                 f"    {v} = new int(2);\n"
                 f"    std::cout << *{v} << std::endl;\n    delete {v};\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = new int(1);\n"
                 f"    delete {v};\n"
                 f"    {v} = new int(2);\n"
                 f"    std::cout << *{v} << std::endl;\n    delete {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 5,
                            f"'{v}' reassigned without deleting the first allocation."))

    # Shape 5: new inside a loop overwrites pointer each iteration
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}(int n) {{\n"
                 f"    int* {v} = nullptr;\n"
                 f"    for (int i = 0; i < n; i++) {{\n"
                 f"        {v} = new int(i);\n    }}\n"
                 f"    if ({v}) delete {v};\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int n) {{\n"
                 f"    int* {v} = nullptr;\n"
                 f"    for (int i = 0; i < n; i++) {{\n"
                 f"        delete {v};\n        {v} = new int(i);\n    }}\n"
                 f"    if ({v}) delete {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 6,
                            f"Each loop iteration overwrites '{v}' without deleting the previous allocation."))

    # Shape 6: new in function, early return leaks memory
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nint {fn}(int {v}) {{\n"
                 f"    int* p = new int({v});\n    int result = *p;\n"
                 f"    return result;\n}}")
        fixed = (f"#include <iostream>\n\nint {fn}(int {v}) {{\n"
                 f"    int* p = new int({v});\n    int result = *p;\n"
                 f"    delete p;\n    return result;\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 6,
                            f"Function '{fn}' returns before deleting heap-allocated pointer 'p'."))

    # Shape 7: new in if-branch, early return skips delete
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}(int {v}) {{\n"
                 f"    int* p = new int({v});\n"
                 f"    if ({v} > {n}) {{\n"
                 f"        std::cout << *p << std::endl;\n        return;\n    }}\n"
                 f"    delete p;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int {v}) {{\n"
                 f"    int* p = new int({v});\n"
                 f"    if ({v} > {n}) {{\n"
                 f"        std::cout << *p << std::endl;\n"
                 f"        delete p;\n        return;\n    }}\n"
                 f"    delete p;\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 7,
                            f"Early return in '{fn}' skips 'delete p'; add delete before return."))

    # Shape 8: struct allocated with new, never freed
    for _ in range(10):
        v, fn, cls = _v(), _m(), _c()
        buggy = (f"#include <iostream>\n\nstruct {cls} {{ int val; }};\n\n"
                 f"void {fn}() {{\n"
                 f"    {cls}* {v} = new {cls}();\n"
                 f"    {v}->val = 42;\n"
                 f"    std::cout << {v}->val << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nstruct {cls} {{ int val; }};\n\n"
                 f"void {fn}() {{\n"
                 f"    {cls}* {v} = new {cls}();\n"
                 f"    {v}->val = 42;\n"
                 f"    std::cout << {v}->val << std::endl;\n    delete {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 7,
                            f"struct {cls}* '{v}' allocated with new but never deleted."))

    # Shape 9: double[] allocated, never freed with delete[]
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}(int n) {{\n"
                 f"    double* {v} = new double[n];\n"
                 f"    for (int i = 0; i < n; i++) {v}[i] = i * 1.5;\n"
                 f"    std::cout << {v}[0] << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int n) {{\n"
                 f"    double* {v} = new double[n];\n"
                 f"    for (int i = 0; i < n; i++) {v}[i] = i * 1.5;\n"
                 f"    std::cout << {v}[0] << std::endl;\n    delete[] {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 4,
                            f"double[] '{v}' never freed; use delete[]."))

    # Shape 10: char[] allocated with new, never deleted
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    char* {v} = new char[64];\n"
                 f"    std::cout << \"allocated\" << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    char* {v} = new char[64];\n"
                 f"    std::cout << \"allocated\" << std::endl;\n    delete[] {v};\n}}")
        s.append(_make_lang(L, buggy, fixed, "memory_leak", 4,
                            f"char[] '{v}' allocated with new[] but never freed."))
    return s


def _gen_cpp_null_pointer_deref() -> list[dict[str, Any]]:
    s, L = [], "cpp"

    # Shape 1: function parameter pointer used without null check
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}(int* {v}) {{\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int* {v}) {{\n"
                 f"    if ({v} == nullptr) return;\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 4,
                            f"Parameter '{v}' may be nullptr; dereferenced without null check."))

    # Shape 2: returned pointer used without null check
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n\nint* get_{v}() {{ return nullptr; }}\n\n"
                 f"void {fn}() {{\n"
                 f"    int* {v} = get_{v}();\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nint* get_{v}() {{ return nullptr; }}\n\n"
                 f"void {fn}() {{\n"
                 f"    int* {v} = get_{v}();\n"
                 f"    if ({v} == nullptr) return;\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 7,
                            f"get_{v}() may return nullptr; result used without null check."))

    # Shape 3: new (nothrow) result not checked
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n#include <new>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = new (std::nothrow) int({n});\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <new>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = new (std::nothrow) int({n});\n"
                 f"    if ({v} == nullptr) return;\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 6,
                            f"new(nothrow) may return nullptr on failure; '{v}' used without check."))

    # Shape 4: explicit nullptr dereference
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = nullptr;\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int* {v} = nullptr;\n"
                 f"    if ({v} != nullptr) {{\n"
                 f"        std::cout << *{v} << std::endl;\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 5,
                            f"'{v}' is explicitly set to nullptr and then dereferenced."))

    # Shape 5: std::string* parameter used without null guard
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <string>\n\n"
                 f"void {fn}(std::string* {v}) {{\n"
                 f"    std::cout << {v}->length() << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <string>\n\n"
                 f"void {fn}(std::string* {v}) {{\n"
                 f"    if ({v} == nullptr) return;\n"
                 f"    std::cout << {v}->length() << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 5,
                            f"std::string* '{v}' may be null; ->length() called without guard."))

    # Shape 6: pointer in vector not checked before dereference
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <vector>\n\n"
                 f"void {fn}(std::vector<int*>& {v}) {{\n"
                 f"    for (int* p : {v}) {{\n"
                 f"        std::cout << *p << std::endl;\n    }}\n}}")
        fixed = (f"#include <iostream>\n#include <vector>\n\n"
                 f"void {fn}(std::vector<int*>& {v}) {{\n"
                 f"    for (int* p : {v}) {{\n"
                 f"        if (p == nullptr) continue;\n"
                 f"        std::cout << *p << std::endl;\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 6,
                            f"Vector '{v}' may contain null pointers; each must be checked."))

    # Shape 7: chained pointer dereference on potentially null next
    for _ in range(10):
        cls, fn = _c(), _m()
        buggy = (f"#include <iostream>\n\nstruct {cls} {{ int val; {cls}* next; }};\n\n"
                 f"void {fn}({cls}* node) {{\n"
                 f"    std::cout << node->next->val << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nstruct {cls} {{ int val; {cls}* next; }};\n\n"
                 f"void {fn}({cls}* node) {{\n"
                 f"    if (node == nullptr || node->next == nullptr) return;\n"
                 f"    std::cout << node->next->val << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 5,
                            f"node->next may be nullptr; chained dereference without null check."))

    # Shape 8: conditional allocation result always used
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nint* alloc_{v}(bool flag) {{\n"
                 f"    if (flag) return new int({n});\n    return nullptr;\n}}\n\n"
                 f"void {fn}() {{\n"
                 f"    int* {v} = alloc_{v}(false);\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nint* alloc_{v}(bool flag) {{\n"
                 f"    if (flag) return new int({n});\n    return nullptr;\n}}\n\n"
                 f"void {fn}() {{\n"
                 f"    int* {v} = alloc_{v}(false);\n"
                 f"    if ({v} == nullptr) return;\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 10,
                            f"alloc_{v}(false) returns nullptr; dereferenced without null check."))

    # Shape 9: class member pointer default initialized to nullptr, used in method
    for _ in range(10):
        v, fn, cls = _v(), _m(), _c()
        buggy = (f"#include <iostream>\n\nclass {cls} {{\n"
                 f"    int* {v} = nullptr;\npublic:\n"
                 f"    void {fn}() {{\n"
                 f"        std::cout << *{v} << std::endl;\n    }}\n}};")
        fixed = (f"#include <iostream>\n\nclass {cls} {{\n"
                 f"    int* {v} = nullptr;\npublic:\n"
                 f"    void {fn}() {{\n"
                 f"        if ({v} == nullptr) return;\n"
                 f"        std::cout << *{v} << std::endl;\n    }}\n}};")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 7,
                            f"Member '{v}' is nullptr by default; dereferenced without null check."))

    # Shape 10: static pointer never initialized, used in function
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n\nstatic int* {v} = nullptr;\n\n"
                 f"void {fn}() {{\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nstatic int* {v} = nullptr;\n\n"
                 f"void {fn}() {{\n"
                 f"    if ({v} == nullptr) return;\n"
                 f"    std::cout << *{v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "null_pointer_deref", 6,
                            f"Static pointer '{v}' is nullptr; used without null check in '{fn}'."))
    return s


def _gen_cpp_wrong_include() -> list[dict[str, Any]]:
    s, L = [], "cpp"

    # Shape 1: simple cout in function, no #include <iostream>
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"void {fn}(int {v}) {{\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int {v}) {{\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 2,
                            f"std::cout used but #include <iostream> is missing."))

    # Shape 2: cout in main, no include
    for _ in range(10):
        v, n = _v(), _n()
        buggy = (f"int main() {{\n"
                 f"    int {v} = {n};\n"
                 f"    std::cout << {v} << std::endl;\n    return 0;\n}}")
        fixed = (f"#include <iostream>\n\nint main() {{\n"
                 f"    int {v} = {n};\n"
                 f"    std::cout << {v} << std::endl;\n    return 0;\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 3,
                            f"std::cout used in main() without #include <iostream>."))

    # Shape 3: cin used without include
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"void {fn}() {{\n"
                 f"    int {v};\n    std::cin >> {v};\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v};\n    std::cin >> {v};\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 3,
                            f"std::cin and std::cout used without #include <iostream>."))

    # Shape 4: cerr used without include
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"void {fn}(int {v}) {{\n"
                 f"    if ({v} < 0) {{\n"
                 f"        std::cerr << \"error\" << std::endl;\n    }}\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int {v}) {{\n"
                 f"    if ({v} < 0) {{\n"
                 f"        std::cerr << \"error\" << std::endl;\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 3,
                            f"std::cerr used without #include <iostream>."))

    # Shape 5: cout with multiple values, no include
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"void {fn}(int {v}, int {v2}) {{\n"
                 f"    std::cout << {v} << \" \" << {v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int {v}, int {v2}) {{\n"
                 f"    std::cout << {v} << \" \" << {v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 2,
                            f"std::cout used in '{fn}' without #include <iostream>."))

    # Shape 6: class method using cout, no include
    for _ in range(10):
        v, fn, cls = _v(), _m(), _c()
        buggy = (f"class {cls} {{\npublic:\n"
                 f"    void {fn}(int {v}) {{\n"
                 f"        std::cout << {v} << std::endl;\n    }}\n}};")
        fixed = (f"#include <iostream>\n\nclass {cls} {{\npublic:\n"
                 f"    void {fn}(int {v}) {{\n"
                 f"        std::cout << {v} << std::endl;\n    }}\n}};")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 4,
                            f"Class method '{cls}::{fn}' uses std::cout without #include <iostream>."))

    # Shape 7: static method using cout, no include
    for _ in range(10):
        v, fn, cls = _v(), _m(), _c()
        buggy = (f"class {cls} {{\npublic:\n"
                 f"    static void {fn}(int {v}) {{\n"
                 f"        std::cout << {v} << std::endl;\n    }}\n}};")
        fixed = (f"#include <iostream>\n\nclass {cls} {{\npublic:\n"
                 f"    static void {fn}(int {v}) {{\n"
                 f"        std::cout << {v} << std::endl;\n    }}\n}};")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 4,
                            f"Static method '{cls}::{fn}' uses std::cout without #include <iostream>."))

    # Shape 8: loop with cout, no include
    for _ in range(10):
        fn, n = _m(), _n()
        buggy = (f"void {fn}(int n) {{\n"
                 f"    for (int i = 0; i < n; i++) {{\n"
                 f"        std::cout << i << std::endl;\n    }}\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int n) {{\n"
                 f"    for (int i = 0; i < n; i++) {{\n"
                 f"        std::cout << i << std::endl;\n    }}\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 3,
                            f"std::cout inside loop in '{fn}' without #include <iostream>."))

    # Shape 9: function returns value and also uses cout, no include
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"int {fn}(int {v}) {{\n"
                 f"    std::cout << \"processing\" << std::endl;\n"
                 f"    return {v} * {n};\n}}")
        fixed = (f"#include <iostream>\n\nint {fn}(int {v}) {{\n"
                 f"    std::cout << \"processing\" << std::endl;\n"
                 f"    return {v} * {n};\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 2,
                            f"std::cout used in '{fn}' without #include <iostream>."))

    # Shape 10: cout and cerr both used, no include
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"void {fn}(int {v}) {{\n"
                 f"    if ({v} >= 0) std::cout << {v} << std::endl;\n"
                 f"    else std::cerr << \"negative\" << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}(int {v}) {{\n"
                 f"    if ({v} >= 0) std::cout << {v} << std::endl;\n"
                 f"    else std::cerr << \"negative\" << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "wrong_include", 2,
                            f"std::cout and std::cerr used in '{fn}' without #include <iostream>."))
    return s


def _gen_cpp_missing_semicolon() -> list[dict[str, Any]]:
    s, L = [], "cpp"

    # Shape 1: int declaration missing ;
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n}\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            f"Missing semicolon after 'int {v} = {n}'."))

    # Shape 2: std::string declaration missing ;
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <string>\n\nvoid {fn}() {{\n"
                 f"    std::string {v} = \"hello\"\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <string>\n\nvoid {fn}() {{\n"
                 f"    std::string {v} = \"hello\";\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after std::string declaration of '{v}'."))

    # Shape 3: return statement missing ;
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nint {fn}(int {v}) {{\n"
                 f"    int result = {v} * {n};\n    return result\n}}")
        fixed = (f"#include <iostream>\n\nint {fn}(int {v}) {{\n"
                 f"    int result = {v} * {n};\n    return result;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            "Missing semicolon after return statement."))

    # Shape 4: std::cout statement missing ;
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n"
                 f"    std::cout << {v} << std::endl\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            "Missing semicolon after std::cout statement."))

    # Shape 5: auto variable declaration missing ;
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    auto {v} = {n}\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    auto {v} = {n};\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 4,
                            f"Missing semicolon after 'auto {v} = {n}'."))

    # Shape 6: assignment statement missing ;
    for _ in range(10):
        v, fn, n, n2 = _v(), _m(), _n(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v} = {v} + {n2}\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v} = {v} + {n2};\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after '{v} = {v} + {n2}'."))

    # Shape 7: method call missing ;
    for _ in range(10):
        v, fn, fn2 = _v(), _m(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn2}() {{ std::cout << \"ok\" << std::endl; }}\n\n"
                 f"void {fn}() {{\n    {fn2}()\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn2}() {{ std::cout << \"ok\" << std::endl; }}\n\n"
                 f"void {fn}() {{\n    {fn2}();\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after '{fn2}()' call."))

    # Shape 8: post-increment missing ;
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v}++\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    {v}++;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after '{v}++'."))

    # Shape 9: std::vector declaration missing ;
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <vector>\n\nvoid {fn}() {{\n"
                 f"    std::vector<int> {v}\n"
                 f"    {v}.push_back(1);\n"
                 f"    std::cout << {v}[0] << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <vector>\n\nvoid {fn}() {{\n"
                 f"    std::vector<int> {v};\n"
                 f"    {v}.push_back(1);\n"
                 f"    std::cout << {v}[0] << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after 'std::vector<int> {v}'."))

    # Shape 10: pointer declaration missing ;
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    int* {v2} = &{v}\n"
                 f"    std::cout << *{v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = {n};\n    int* {v2} = &{v};\n"
                 f"    std::cout << *{v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "missing_semicolon", 5,
                            f"Missing semicolon after 'int* {v2} = &{v}'."))
    return s


def _gen_cpp_undefined_behaviour() -> list[dict[str, Any]]:
    s, L = [], "cpp"

    # Shape 1: INT_MAX + 1 stored in int
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int {v} = INT_MAX;\n    {v}++;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = INT_MAX;\n    {v}++;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 6,
                            f"'{v}++' overflows INT_MAX; use long long to avoid UB."))

    # Shape 2: multiplication overflow
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = 100000;\n"
                 f"    int {v2} = {v} * {v};\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = 100000;\n"
                 f"    long long {v2} = {v} * {v};\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 5,
                            f"{v}*{v} = 10^10 overflows int; use long long."))

    # Shape 3: INT_MAX + 1 direct literal
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int {v} = INT_MAX + 1;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = (long long)INT_MAX + 1;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 5,
                            f"INT_MAX + 1 overflows signed int; cast to long long first."))

    # Shape 4: negation of INT_MIN
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int {v} = INT_MIN;\n    int {v2} = -{v};\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = INT_MIN;\n    long long {v2} = -{v};\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 6,
                            f"-INT_MIN overflows signed int; use long long."))

    # Shape 5: left-shift into sign bit
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = 1;\n    int {v2} = {v} << 31;\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    unsigned int {v} = 1u;\n    unsigned int {v2} = {v} << 31;\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 5,
                            f"Shifting signed int into sign bit is UB; use unsigned int."))

    # Shape 6: accumulator overflow in a loop
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(3, 10)
        buggy = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int {v} = INT_MAX - {n};\n"
                 f"    for (int i = 0; i <= {n} + 1; i++) {v}++;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = INT_MAX - {n};\n"
                 f"    for (int i = 0; i <= {n} + 1; i++) {v}++;\n"
                 f"    std::cout << {v} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 5,
                            f"Loop increments '{v}' past INT_MAX; use long long."))

    # Shape 7: subtraction underflow (INT_MIN - 1)
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int {v} = INT_MIN;\n    int {v2} = {v} - 1;\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = INT_MIN;\n    long long {v2} = {v} - 1;\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 6,
                            f"INT_MIN - 1 underflows signed int; use long long."))

    # Shape 8: shift by type width (UB)
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = 1;\n    int {v2} = {v} << 32;\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = 1LL;\n    long long {v2} = {v} << 32;\n"
                 f"    std::cout << {v2} << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 5,
                            f"Shifting int by 32 (its bit width) is undefined behaviour."))

    # Shape 9: array index computed from overflowing arithmetic
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(3, 8)
        buggy = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int arr[{n}] = {{0}};\n"
                 f"    int idx = INT_MAX + 1;\n"
                 f"    std::cout << arr[idx % {n}] << std::endl;\n}}")
        fixed = (f"#include <iostream>\n#include <climits>\n\nvoid {fn}() {{\n"
                 f"    int arr[{n}] = {{0}};\n"
                 f"    long long idx = (long long)INT_MAX + 1;\n"
                 f"    std::cout << arr[idx % {n}] << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 6,
                            f"Array index computed from INT_MAX + 1; overflow causes UB."))

    # Shape 10: large multiplication stored in int without cast
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    int {v} = 50000;\n    int {v2} = 50000;\n"
                 f"    int result = {v} * {v2};\n"
                 f"    std::cout << result << std::endl;\n}}")
        fixed = (f"#include <iostream>\n\nvoid {fn}() {{\n"
                 f"    long long {v} = 50000;\n    long long {v2} = 50000;\n"
                 f"    long long result = {v} * {v2};\n"
                 f"    std::cout << result << std::endl;\n}}")
        s.append(_make_lang(L, buggy, fixed, "undefined_behaviour", 6,
                            f"50000 * 50000 = 2.5×10^9 overflows int; use long long."))
    return s


def generate_cpp_samples() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gen in [_gen_cpp_memory_leak, _gen_cpp_null_pointer_deref,
                _gen_cpp_wrong_include, _gen_cpp_missing_semicolon,
                _gen_cpp_undefined_behaviour]:
        buggy = gen()
        assert len(buggy) == 100, f"{gen.__name__} produced {len(buggy)} samples"
        rows.extend(buggy)
        rows.extend(_to_clean(s) for s in buggy)
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Python — bug generators (10 shapes × 10 variants = 100 per bug type)
# ─────────────────────────────────────────────────────────────────────────────

def _gen_py_index_out_of_range() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: lst[len(lst)] — classic off-by-one
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = [1, 2, 3, 4, 5]\n"
                 f"    last = {v}[len({v})]\n"
                 f"    print(last)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = [1, 2, 3, 4, 5]\n"
                 f"    last = {v}[-1]\n"
                 f"    print(last)")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"lst[len(lst)] is one past the end; use lst[-1]."))

    # Shape 2: hard-coded index equals list size
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(3, 8)
        buggy = (f"def {fn}():\n"
                 f"    {v} = list(range({n}))\n"
                 f"    print({v}[{n}])")
        fixed = (f"def {fn}():\n"
                 f"    {v} = list(range({n}))\n"
                 f"    print({v}[{n} - 1])")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"Index {n} equals list size; valid range is 0 to {n-1}."))

    # Shape 3: accessing first element of empty list
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = []\n"
                 f"    first = {v}[0]\n"
                 f"    print(first)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = []\n"
                 f"    if {v}:\n"
                 f"        first = {v}[0]\n"
                 f"        print(first)")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"'{v}' is empty; {v}[0] raises IndexError."))

    # Shape 4: negative index beyond list length
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(3, 6)
        buggy = (f"def {fn}():\n"
                 f"    {v} = [10, 20, 30]\n"
                 f"    val = {v}[-{n}]\n"
                 f"    print(val)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = [10, 20, 30]\n"
                 f"    val = {v}[-1]\n"
                 f"    print(val)")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"Negative index -{n} exceeds the list length of 3."))

    # Shape 5: string index out of range
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = \"hello\"\n"
                 f"    ch = {v}[10]\n"
                 f"    print(ch)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = \"hello\"\n"
                 f"    if len({v}) > 10:\n"
                 f"        ch = {v}[10]\n"
                 f"        print(ch)")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"String '{v}' has length 5; index 10 is out of range."))

    # Shape 6: tuple index out of range
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(5, 10)
        buggy = (f"def {fn}():\n"
                 f"    {v} = (1, 2, 3)\n"
                 f"    val = {v}[{n}]\n"
                 f"    print(val)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = (1, 2, 3)\n"
                 f"    val = {v}[2]\n"
                 f"    print(val)")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"Tuple '{v}' has 3 elements; index {n} is out of range."))

    # Shape 7: index from variable equals length
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    n = len({v})\n"
                 f"    last = {v}[n]\n"
                 f"    print(last)")
        fixed = (f"def {fn}({v}):\n"
                 f"    n = len({v})\n"
                 f"    last = {v}[n - 1]\n"
                 f"    print(last)")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"{v}[n] where n = len({v}) is one past the last element."))

    # Shape 8: while loop with <= instead of <
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(3, 8)
        buggy = (f"def {fn}():\n"
                 f"    {v} = list(range({n}))\n"
                 f"    i = 0\n"
                 f"    while i <= len({v}):\n"
                 f"        print({v}[i])\n"
                 f"        i += 1")
        fixed = (f"def {fn}():\n"
                 f"    {v} = list(range({n}))\n"
                 f"    i = 0\n"
                 f"    while i < len({v}):\n"
                 f"        print({v}[i])\n"
                 f"        i += 1")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 4,
                            f"Condition 'i <= len({v})' accesses index len({v}), which is out of range."))

    # Shape 9: slice result indexed beyond its size
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = [1, 2, 3, 4, 5]\n"
                 f"    {v2} = {v}[2:4]\n"
                 f"    print({v2}[2])")
        fixed = (f"def {fn}():\n"
                 f"    {v} = [1, 2, 3, 4, 5]\n"
                 f"    {v2} = {v}[2:4]\n"
                 f"    print({v2}[-1])")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 4,
                            f"Slice {v}[2:4] has 2 elements; index 2 is out of range."))

    # Shape 10: list comprehension result indexed with original size
    for _ in range(10):
        v, fn, n = _v(), _m(), _n(4, 10)
        buggy = (f"def {fn}():\n"
                 f"    {v} = [i * 2 for i in range({n})]\n"
                 f"    print({v}[{n}])")
        fixed = (f"def {fn}():\n"
                 f"    {v} = [i * 2 for i in range({n})]\n"
                 f"    print({v}[-1])")
        s.append(_make_lang(L, buggy, fixed, "index_out_of_range", 3,
                            f"List '{v}' has {n} elements; index {n} is out of range."))
    return s


def _gen_py_missing_return() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: function prints instead of returning
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    result = {v} * 2\n"
                 f"    print(result)")
        fixed = (f"def {fn}({v}):\n"
                 f"    result = {v} * 2\n"
                 f"    return result")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 3,
                            f"'{fn}' prints instead of returning the result."))

    # Shape 2: function computes but has no return statement
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"def {fn}({v}, {v2}):\n"
                 f"    total = {v} + {v2}\n"
                 f"    scaled = total * {n}")
        fixed = (f"def {fn}({v}, {v2}):\n"
                 f"    total = {v} + {v2}\n"
                 f"    scaled = total * {n}\n"
                 f"    return scaled")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 4,
                            f"'{fn}' computes 'scaled' but never returns it."))

    # Shape 3: return only in if branch, implicit None in else
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    if {v} > {n}:\n"
                 f"        return {v}")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} > {n}:\n"
                 f"        return {v}\n"
                 f"    return 0")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 4,
                            f"'{fn}' returns only when {v} > {n}; implicit None otherwise."))

    # Shape 4: multiple elif branches, default case missing return
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    if {v} == 'a':\n"
                 f"        return 1\n"
                 f"    elif {v} == 'b':\n"
                 f"        return 2")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} == 'a':\n"
                 f"        return 1\n"
                 f"    elif {v} == 'b':\n"
                 f"        return 2\n"
                 f"    return 0")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"'{fn}' has no return for the default case; returns None."))

    # Shape 5: recursive function missing base-case return
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    if {v} > 0:\n"
                 f"        return {fn}({v} - 1)")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} <= 0:\n"
                 f"        return 0\n"
                 f"    return {fn}({v} - 1)")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 4,
                            f"Recursive '{fn}' has no base-case return; returns None when {v} <= 0."))

    # Shape 6: try returns but except does not
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    try:\n"
                 f"        return int({v})\n"
                 f"    except ValueError:\n"
                 f"        print(\"invalid\")")
        fixed = (f"def {fn}({v}):\n"
                 f"    try:\n"
                 f"        return int({v})\n"
                 f"    except ValueError:\n"
                 f"        print(\"invalid\")\n"
                 f"        return 0")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 5,
                            f"'{fn}' returns in try but not in except; implicitly returns None on error."))

    # Shape 7: for loop with return inside might not execute
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"def {fn}({v}, {v2}):\n"
                 f"    for item in {v}:\n"
                 f"        if item == {v2}:\n"
                 f"            return item")
        fixed = (f"def {fn}({v}, {v2}):\n"
                 f"    for item in {v}:\n"
                 f"        if item == {v2}:\n"
                 f"            return item\n"
                 f"    return None")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 5,
                            f"'{fn}' only returns if target found; returns None implicitly when not found."))

    # Shape 8: computes list but doesn't return it
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    results = [x * {n} for x in {v}]\n"
                 f"    filtered = [x for x in results if x > 0]")
        fixed = (f"def {fn}({v}):\n"
                 f"    results = [x * {n} for x in {v}]\n"
                 f"    filtered = [x for x in results if x > 0]\n"
                 f"    return filtered")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 4,
                            f"'{fn}' computes 'filtered' but never returns it."))

    # Shape 9: helper used inside but outer function doesn't return
    for _ in range(10):
        v, fn, fn2, n = _v(), _m(), _m(), _n()
        buggy = (f"def {fn2}(x):\n"
                 f"    return x * {n}\n\n"
                 f"def {fn}({v}):\n"
                 f"    processed = [{fn2}(x) for x in {v}]")
        fixed = (f"def {fn2}(x):\n"
                 f"    return x * {n}\n\n"
                 f"def {fn}({v}):\n"
                 f"    processed = [{fn2}(x) for x in {v}]\n"
                 f"    return processed")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 6,
                            f"'{fn}' uses helper but never returns the processed result."))

    # Shape 10: while loop with return inside, falls through at end
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    i = 0\n"
                 f"    while i < {v}:\n"
                 f"        if i == {n}:\n"
                 f"            return i\n"
                 f"        i += 1")
        fixed = (f"def {fn}({v}):\n"
                 f"    i = 0\n"
                 f"    while i < {v}:\n"
                 f"        if i == {n}:\n"
                 f"            return i\n"
                 f"        i += 1\n"
                 f"    return -1")
        s.append(_make_lang(L, buggy, fixed, "missing_return", 7,
                            f"'{fn}' returns inside the loop but has no return after it."))
    return s


def _gen_py_type_error() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: str + int concatenation
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    msg = \"count: \" + {v}\n"
                 f"    print(msg)")
        fixed = (f"def {fn}({v}):\n"
                 f"    msg = \"count: \" + str({v})\n"
                 f"    print(msg)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 2,
                            f"str + int: cannot concatenate str with {v}; use str({v})."))

    # Shape 2: int + str concatenation
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    total = 10 + {v}\n"
                 f"    print(total)")
        fixed = (f"def {fn}({v}):\n"
                 f"    total = 10 + int({v})\n"
                 f"    print(total)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 2,
                            f"int + str: '10 + {v}' fails if {v} is a string; use int({v})."))

    # Shape 3: float + str concatenation
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 3.14\n"
                 f"    label = {v} + \" kg\"\n"
                 f"    print(label)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 3.14\n"
                 f"    label = str({v}) + \" kg\"\n"
                 f"    print(label)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 3,
                            f"float + str: '{v} + \" kg\"' raises TypeError; use str({v})."))

    # Shape 4: list + str concatenation
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = [\"a\", \"b\", \"c\"]\n"
                 f"    result = {v} + \"d\"\n"
                 f"    print(result)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = [\"a\", \"b\", \"c\"]\n"
                 f"    result = {v} + [\"d\"]\n"
                 f"    print(result)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 3,
                            f"list + str: '{v} + \"d\"' raises TypeError; use {v} + [\"d\"]."))

    # Shape 5: calling str method on int
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = {n}\n"
                 f"    upper = {v}.upper()\n"
                 f"    print(upper)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = {n}\n"
                 f"    upper = str({v}).upper()\n"
                 f"    print(upper)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 3,
                            f"int has no .upper(); convert {v} to str first."))

    # Shape 6: None + int
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = None\n"
                 f"    result = {v} + {n}\n"
                 f"    print(result)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    result = {v} + {n}\n"
                 f"    print(result)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 3,
                            f"NoneType + int: '{v} + {n}' raises TypeError; initialise {v} to 0."))

    # Shape 7: str * str (should be str * int)
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = \"3\"\n"
                 f"    result = \"ha\" * {v}\n"
                 f"    print(result)")
        fixed = (f"def {fn}():\n"
                 f"    {v} = \"3\"\n"
                 f"    result = \"ha\" * int({v})\n"
                 f"    print(result)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 3,
                            f"str * str: '\"ha\" * {v}' raises TypeError; use int({v})."))

    # Shape 8: comparing int < str
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    if {v} < \"{n}\":\n"
                 f"        print(\"small\")\n"
                 f"    else:\n"
                 f"        print(\"large\")")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} < {n}:\n"
                 f"        print(\"small\")\n"
                 f"    else:\n"
                 f"        print(\"large\")")
        s.append(_make_lang(L, buggy, fixed, "type_error", 2,
                            f"Comparing int '{v}' with str '\"{n}\"' raises TypeError in Python 3."))

    # Shape 9: passing str to math.sqrt
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"import math\n\n"
                 f"def {fn}():\n"
                 f"    {v} = \"4.0\"\n"
                 f"    result = math.sqrt({v})\n"
                 f"    print(result)")
        fixed = (f"import math\n\n"
                 f"def {fn}():\n"
                 f"    {v} = \"4.0\"\n"
                 f"    result = math.sqrt(float({v}))\n"
                 f"    print(result)")
        s.append(_make_lang(L, buggy, fixed, "type_error", 5,
                            f"math.sqrt expects a number; '{v}' is a str; use float({v})."))

    # Shape 10: accumulating int with str items in a loop
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    for item in [\"1\", \"2\", \"3\"]:\n"
                 f"        {v} += item\n"
                 f"    print({v})")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    for item in [\"1\", \"2\", \"3\"]:\n"
                 f"        {v} += int(item)\n"
                 f"    print({v})")
        s.append(_make_lang(L, buggy, fixed, "type_error", 4,
                            f"'{v} += item' fails when item is str; use int(item)."))
    return s


def _gen_py_undefined_variable() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: variable used before assignment in function body
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    print({v})\n"
                 f"    {v} = {n}")
        fixed = (f"def {fn}():\n"
                 f"    {v} = {n}\n"
                 f"    print({v})")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 2,
                            f"'{v}' used before it is assigned (NameError)."))

    # Shape 2: conditional assignment, used unconditionally
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"def {fn}({v2}):\n"
                 f"    if {v2} > {n}:\n"
                 f"        {v} = {v2} * 2\n"
                 f"    print({v})")
        fixed = (f"def {fn}({v2}):\n"
                 f"    {v} = 0\n"
                 f"    if {v2} > {n}:\n"
                 f"        {v} = {v2} * 2\n"
                 f"    print({v})")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 4,
                            f"'{v}' only assigned when {v2} > {n}; NameError when condition is False."))

    # Shape 3: typo in variable name
    for _ in range(10):
        fn, n = _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    username = \"alice\"\n"
                 f"    print(user_name)")
        fixed = (f"def {fn}():\n"
                 f"    username = \"alice\"\n"
                 f"    print(username)")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 3,
                            "'user_name' is a typo for 'username'; NameError at runtime."))

    # Shape 4: variable defined inside if block, used outside
    for _ in range(10):
        v, v2, fn = _v(), _v(), _m()
        buggy = (f"def {fn}(flag):\n"
                 f"    if flag:\n"
                 f"        {v} = 42\n"
                 f"    print({v})")
        fixed = (f"def {fn}(flag):\n"
                 f"    {v} = None\n"
                 f"    if flag:\n"
                 f"        {v} = 42\n"
                 f"    print({v})")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 4,
                            f"'{v}' only defined when flag is True; NameError when False."))

    # Shape 5: loop variable name typo outside loop
    for _ in range(10):
        fn = _m()
        buggy = (f"def {fn}():\n"
                 f"    for item in range(10):\n"
                 f"        pass\n"
                 f"    print(items)")
        fixed = (f"def {fn}():\n"
                 f"    for item in range(10):\n"
                 f"        pass\n"
                 f"    print(item)")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 4,
                            "'items' is a typo; the loop variable is 'item'."))

    # Shape 6: try block variable, used after except when exception occurs
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(s):\n"
                 f"    try:\n"
                 f"        {v} = int(s)\n"
                 f"    except ValueError:\n"
                 f"        pass\n"
                 f"    print({v})")
        fixed = (f"def {fn}(s):\n"
                 f"    {v} = 0\n"
                 f"    try:\n"
                 f"        {v} = int(s)\n"
                 f"    except ValueError:\n"
                 f"        pass\n"
                 f"    print({v})")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 6,
                            f"'{v}' may be unset if ValueError is raised; initialise before try."))

    # Shape 7: global name that was never defined
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    print(DEFAULT_{v.upper()})")
        fixed = (f"DEFAULT_{v.upper()} = {n}\n\n"
                 f"def {fn}():\n"
                 f"    print(DEFAULT_{v.upper()})")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 2,
                            f"'DEFAULT_{v.upper()}' is used but never defined (NameError)."))

    # Shape 8: parameter named differently than body expects
    for _ in range(10):
        v, fn = _v(), _m()
        v2 = v + "_input"
        buggy = (f"def {fn}({v2}):\n"
                 f"    processed = {v}.strip()\n"
                 f"    return processed")
        fixed = (f"def {fn}({v2}):\n"
                 f"    processed = {v2}.strip()\n"
                 f"    return processed")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 2,
                            f"Body uses '{v}' but parameter is '{v2}' (NameError)."))

    # Shape 9: variable defined only in else, used after if/else
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"def {fn}({v2}):\n"
                 f"    if {v2} > {n}:\n"
                 f"        pass\n"
                 f"    else:\n"
                 f"        {v} = {v2} - {n}\n"
                 f"    print({v})")
        fixed = (f"def {fn}({v2}):\n"
                 f"    {v} = 0\n"
                 f"    if {v2} > {n}:\n"
                 f"        pass\n"
                 f"    else:\n"
                 f"        {v} = {v2} - {n}\n"
                 f"    print({v})")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 6,
                            f"'{v}' only assigned in else; NameError when {v2} > {n}."))

    # Shape 10: forgot to unpack tuple before using element
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    data = (1, 2, 3)\n"
                 f"    print(x)")
        fixed = (f"def {fn}():\n"
                 f"    data = (1, 2, 3)\n"
                 f"    x, y, z = data\n"
                 f"    print(x)")
        s.append(_make_lang(L, buggy, fixed, "undefined_variable", 3,
                            "'x' is used but data was never unpacked; add 'x, y, z = data'."))
    return s


def _gen_py_infinite_loop() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: while True with no break
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    while True:\n"
                 f"        print(\"{v}\")")
        fixed = (f"def {fn}():\n"
                 f"    count = 0\n"
                 f"    while count < 100:\n"
                 f"        print(\"{v}\")\n"
                 f"        count += 1")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 2,
                            f"while True with no break in '{fn}'; loop runs forever."))

    # Shape 2: flag never set to False inside loop
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = True\n"
                 f"    while {v}:\n"
                 f"        print(\"looping\")")
        fixed = (f"def {fn}():\n"
                 f"    {v} = True\n"
                 f"    count = 0\n"
                 f"    while {v} and count < 100:\n"
                 f"        print(\"looping\")\n"
                 f"        count += 1\n"
                 f"    {v} = False")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 3,
                            f"Flag '{v}' is never set to False inside the loop."))

    # Shape 3: counter not incremented
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    i = 0\n"
                 f"    while i < {v}:\n"
                 f"        print(i)")
        fixed = (f"def {fn}({v}):\n"
                 f"    i = 0\n"
                 f"    while i < {v}:\n"
                 f"        print(i)\n"
                 f"        i += 1")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 3,
                            f"Counter 'i' is never incremented; 'i < {v}' never becomes False."))

    # Shape 4: counter decremented instead of incremented
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        print({v})\n"
                 f"        {v} -= 1")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        print({v})\n"
                 f"        {v} += 1")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 5,
                            f"'{v} -= 1' moves away from {n}; condition '{v} < {n}' never becomes False."))

    # Shape 5: break inside dead code (if False)
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while True:\n"
                 f"        {v} += 1\n"
                 f"        if False:\n"
                 f"            break")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while True:\n"
                 f"        {v} += 1\n"
                 f"        if {v} >= 100:\n"
                 f"            break")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 5,
                            f"break is inside 'if False' which never executes; loop runs forever."))

    # Shape 6: recursive function with no base case
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}({v}):\n"
                 f"    return {fn}({v} - 1)")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} <= 0:\n"
                 f"        return 0\n"
                 f"    return {fn}({v} - 1)")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 2,
                            f"'{fn}' has no base case; recursion never terminates."))

    # Shape 7: flag always reset to True inside loop
    for _ in range(10):
        v, v2, fn, n = _v(), _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = True\n"
                 f"    {v2} = 0\n"
                 f"    while {v}:\n"
                 f"        {v2} += 1\n"
                 f"        {v} = True")
        fixed = (f"def {fn}():\n"
                 f"    {v} = True\n"
                 f"    {v2} = 0\n"
                 f"    while {v}:\n"
                 f"        {v2} += 1\n"
                 f"        if {v2} >= {n}:\n"
                 f"            {v} = False")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 6,
                            f"'{v}' is always reset to True; loop never terminates."))

    # Shape 8: counter computed but variable not updated
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        print({v})\n"
                 f"        j = {v} + 1")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        print({v})\n"
                 f"        {v} += 1")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 5,
                            f"'j = {v} + 1' computes next value but '{v}' is never updated."))

    # Shape 9: loop variable always reset to initial value inside body
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 1\n"
                 f"    while {v} != 0:\n"
                 f"        print({v})\n"
                 f"        {v} = 1")
        fixed = (f"def {fn}():\n"
                 f"    {v} = {n}\n"
                 f"    while {v} != 0:\n"
                 f"        print({v})\n"
                 f"        {v} -= 1")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 5,
                            f"'{v}' is always reset to 1 inside loop; condition '{v} != 0' is always True."))

    # Shape 10: continue skips the increment statement
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        if {v} % 2 == 0:\n"
                 f"            print({v})\n"
                 f"            continue\n"
                 f"        {v} += 1")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        if {v} % 2 == 0:\n"
                 f"            print({v})\n"
                 f"        {v} += 1")
        s.append(_make_lang(L, buggy, fixed, "infinite_loop", 6,
                            f"'continue' skips '{v} += 1' when {v} is even; loop hangs on first even value."))
    return s


def _gen_py_mutable_default_arg() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: def fn(x, lst=[]) with append
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(x, {v}=[]):\n"
                 f"    {v}.append(x)\n"
                 f"    return {v}")
        fixed = (f"def {fn}(x, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = []\n"
                 f"    {v}.append(x)\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Mutable default list '{v}=[]' is shared across calls; use None."))

    # Shape 2: def fn(x, d={}) with dict update
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(key, val, {v}={{}}):\n"
                 f"    {v}[key] = val\n"
                 f"    return {v}")
        fixed = (f"def {fn}(key, val, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = {{}}\n"
                 f"    {v}[key] = val\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Mutable default dict '{v}={{}}' is shared across calls; use None."))

    # Shape 3: def fn(item, seen=set())
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(item, {v}=set()):\n"
                 f"    {v}.add(item)\n"
                 f"    return {v}")
        fixed = (f"def {fn}(item, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = set()\n"
                 f"    {v}.add(item)\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Mutable default set '{v}=set()' is shared across calls; use None."))

    # Shape 4: class __init__ with mutable default
    for _ in range(10):
        v, cls = _v(), _c()
        buggy = (f"class {cls}:\n"
                 f"    def __init__(self, items=[]):\n"
                 f"        self.{v} = items\n\n"
                 f"    def add(self, item):\n"
                 f"        self.{v}.append(item)")
        fixed = (f"class {cls}:\n"
                 f"    def __init__(self, items=None):\n"
                 f"        self.{v} = items if items is not None else []\n\n"
                 f"    def add(self, item):\n"
                 f"        self.{v}.append(item)")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 2,
                            f"Mutable default list 'items=[]' in {cls}.__init__ shared across instances."))

    # Shape 5: accumulator with mutable default
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(n, {v}=[]):\n"
                 f"    {v}.append(n * 2)\n"
                 f"    return {v}")
        fixed = (f"def {fn}(n, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = []\n"
                 f"    {v}.append(n * 2)\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Default list '{v}=[]' accumulates state between calls."))

    # Shape 6: cache using mutable default list
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(data, cache=[]):\n"
                 f"    if data not in cache:\n"
                 f"        cache.append(data)\n"
                 f"    return cache")
        fixed = (f"def {fn}(data, cache=None):\n"
                 f"    if cache is None:\n"
                 f"        cache = []\n"
                 f"    if data not in cache:\n"
                 f"        cache.append(data)\n"
                 f"    return cache")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            "Default list 'cache=[]' persists across calls; use None."))

    # Shape 7: multi-key dict accumulation
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(key, value, {v}={{}}):\n"
                 f"    if key not in {v}:\n"
                 f"        {v}[key] = []\n"
                 f"    {v}[key].append(value)\n"
                 f"    return {v}")
        fixed = (f"def {fn}(key, value, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = {{}}\n"
                 f"    if key not in {v}:\n"
                 f"        {v}[key] = []\n"
                 f"    {v}[key].append(value)\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Mutable default dict '{v}={{}}' shared across calls; use None."))

    # Shape 8: bytearray mutable default
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(data, {v}=bytearray()):\n"
                 f"    {v}.extend(data)\n"
                 f"    return {v}")
        fixed = (f"def {fn}(data, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = bytearray()\n"
                 f"    {v}.extend(data)\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Mutable default bytearray '{v}=bytearray()' shared across calls."))

    # Shape 9: tracking seen items with mutable default
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(item, {v}=[]):\n"
                 f"    if item in {v}:\n"
                 f"        return False\n"
                 f"    {v}.append(item)\n"
                 f"    return True")
        fixed = (f"def {fn}(item, {v}=None):\n"
                 f"    if {v} is None:\n"
                 f"        {v} = []\n"
                 f"    if item in {v}:\n"
                 f"        return False\n"
                 f"    {v}.append(item)\n"
                 f"    return True")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 1,
                            f"Default list '{v}=[]' persists seen items across invocations."))

    # Shape 10: class method with mutable default history
    for _ in range(10):
        v, fn, cls = _v(), _m(), _c()
        buggy = (f"class {cls}:\n"
                 f"    def {fn}(self, item, history=[]):\n"
                 f"        history.append(item)\n"
                 f"        return history")
        fixed = (f"class {cls}:\n"
                 f"    def {fn}(self, item, history=None):\n"
                 f"        if history is None:\n"
                 f"            history = []\n"
                 f"        history.append(item)\n"
                 f"        return history")
        s.append(_make_lang(L, buggy, fixed, "mutable_default_arg", 2,
                            f"Method '{cls}.{fn}' uses mutable default 'history=[]'; shared across instances."))
    return s


def _gen_py_indentation_error() -> list[dict[str, Any]]:
    s, L = [], "python"

    # Shape 1: return dedented outside function body
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    x = {v} * {n}\n"
                 f"return x")
        fixed = (f"def {fn}({v}):\n"
                 f"    x = {v} * {n}\n"
                 f"    return x")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 3,
                            f"'return x' is outside the function body; indent it 4 spaces."))

    # Shape 2: if body not indented
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    if {v} > {n}:\n"
                 f"    print(\"yes\")")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} > {n}:\n"
                 f"        print(\"yes\")")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 3,
                            f"if body 'print(\"yes\")' must be indented under the if clause."))

    # Shape 3: for loop body not indented
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    for i in range({n}):\n"
                 f"    print(i)")
        fixed = (f"def {fn}():\n"
                 f"    for i in range({n}):\n"
                 f"        print(i)")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 3,
                            "for loop body 'print(i)' must be indented inside the loop."))

    # Shape 4: else clause at wrong (function) level
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"    if {v} > {n}:\n"
                 f"        return \"big\"\n"
                 f"else:\n"
                 f"    return \"small\"")
        fixed = (f"def {fn}({v}):\n"
                 f"    if {v} > {n}:\n"
                 f"        return \"big\"\n"
                 f"    else:\n"
                 f"        return \"small\"")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 4,
                            "else clause is at module level; should be indented 4 spaces."))

    # Shape 5: function body not indented at all
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}({v}):\n"
                 f"result = {v} + {n}\n"
                 f"return result")
        fixed = (f"def {fn}({v}):\n"
                 f"    result = {v} + {n}\n"
                 f"    return result")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 2,
                            "Function body at column 0; both statements need 4-space indent."))

    # Shape 6: nested if inner block not indented
    for _ in range(10):
        v, v2, fn, n, n2 = _v(), _v(), _m(), _n(), _n()
        buggy = (f"def {fn}({v}, {v2}):\n"
                 f"    if {v} > {n}:\n"
                 f"        if {v2} > {n2}:\n"
                 f"        return True\n"
                 f"    return False")
        fixed = (f"def {fn}({v}, {v2}):\n"
                 f"    if {v} > {n}:\n"
                 f"        if {v2} > {n2}:\n"
                 f"            return True\n"
                 f"    return False")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 4,
                            "Inner 'return True' must be indented 12 spaces under nested if."))

    # Shape 7: while body not indented
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"    print({v})\n"
                 f"    {v} += 1")
        fixed = (f"def {fn}():\n"
                 f"    {v} = 0\n"
                 f"    while {v} < {n}:\n"
                 f"        print({v})\n"
                 f"        {v} += 1")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 4,
                            f"while body must be indented; 'print' and '{v} += 1' are at wrong level."))

    # Shape 8: class method not indented relative to class
    for _ in range(10):
        v, fn, cls = _v(), _m(), _c()
        buggy = (f"class {cls}:\n"
                 f"def {fn}(self, {v}):\n"
                 f"    return {v} * 2")
        fixed = (f"class {cls}:\n"
                 f"    def {fn}(self, {v}):\n"
                 f"        return {v} * 2")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 2,
                            f"Method '{fn}' must be indented inside class {cls}."))

    # Shape 9: try body not indented
    for _ in range(10):
        v, fn = _v(), _m()
        buggy = (f"def {fn}(s):\n"
                 f"    try:\n"
                 f"    {v} = int(s)\n"
                 f"    except ValueError:\n"
                 f"        {v} = 0\n"
                 f"    return {v}")
        fixed = (f"def {fn}(s):\n"
                 f"    try:\n"
                 f"        {v} = int(s)\n"
                 f"    except ValueError:\n"
                 f"        {v} = 0\n"
                 f"    return {v}")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 3,
                            f"try body '{v} = int(s)' must be indented inside the try block."))

    # Shape 10: code after loop at wrong level (logical indentation bug)
    for _ in range(10):
        v, fn, n = _v(), _m(), _n()
        buggy = (f"def {fn}():\n"
                 f"    total = 0\n"
                 f"    for i in range({n}):\n"
                 f"        total += i\n"
                 f"    print(i)\n"
                 f"    return total")
        fixed = (f"def {fn}():\n"
                 f"    total = 0\n"
                 f"    for i in range({n}):\n"
                 f"        total += i\n"
                 f"        print(i)\n"
                 f"    return total")
        s.append(_make_lang(L, buggy, fixed, "indentation_error", 5,
                            f"'print(i)' at line 5 is outside the loop; indent 8 spaces to put it inside."))
    return s


def generate_python_samples() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for gen in [_gen_py_index_out_of_range, _gen_py_missing_return,
                _gen_py_type_error, _gen_py_undefined_variable,
                _gen_py_infinite_loop, _gen_py_mutable_default_arg,
                _gen_py_indentation_error]:
        buggy = gen()
        assert len(buggy) == 100, f"{gen.__name__} produced {len(buggy)} samples"
        rows.extend(buggy)
        rows.extend(_to_clean(s) for s in buggy)
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from collections import Counter

    ALL_OUTPUT = os.path.join("data", "training_data.csv")

    print("Generating Java samples  ...", end="", flush=True)
    java_rows   = generate_java_samples()
    print(f" {len(java_rows):>5} rows")

    print("Generating C samples     ...", end="", flush=True)
    c_rows      = generate_c_samples()
    print(f" {len(c_rows):>5} rows")

    print("Generating C++ samples   ...", end="", flush=True)
    cpp_rows    = generate_cpp_samples()
    print(f" {len(cpp_rows):>5} rows")

    print("Generating Python samples...", end="", flush=True)
    python_rows = generate_python_samples()
    print(f" {len(python_rows):>5} rows")

    all_samples = java_rows + c_rows + cpp_rows + python_rows
    random.shuffle(all_samples)

    # ── Per-language counts ──────────────────────────────────────────────────
    lang_counts: Counter = Counter(s["language"] for s in all_samples)
    bug_counts:  Counter = Counter(
        f"{s['language']}/{s['bug_type']}" for s in all_samples if s["is_bug"] == 1
    )
    is_bug_counts: Counter = Counter(s["is_bug"] for s in all_samples)

    print()
    print(f"{'Language':<12} {'rows':>6}")
    print("-" * 20)
    for lang in ["java", "c", "cpp", "python"]:
        print(f"  {lang:<10} {lang_counts[lang]:>6}")

    print()
    print(f"{'bug_type (language/type)':<40} {'count':>6}")
    print("-" * 48)
    for bt, cnt in sorted(bug_counts.items()):
        print(f"  {bt:<38} {cnt:>6}")

    print()
    buggy_n = is_bug_counts[1]
    clean_n = is_bug_counts[0]
    total_n = len(all_samples)
    print(f"Total samples: {total_n}")
    print(f"Buggy: {buggy_n},  Clean: {clean_n}")

    save_to_csv(all_samples, ALL_OUTPUT)
    print(f"\nSaved -> {ALL_OUTPUT}")
