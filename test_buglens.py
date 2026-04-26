import unittest
import requests

BASE = "http://localhost:5000"


class TestAPIHealth(unittest.TestCase):
    def test_health_endpoint(self):
        r = requests.get(f"{BASE}/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("models_loaded", data, "Response missing 'models_loaded' key")
        self.assertTrue(data["models_loaded"], "models_loaded is False — models may not have loaded correctly")


class TestCleanCode(unittest.TestCase):
    def test_clean_java(self):
        code = """
public class HelloWorld {
    public static void main(String[] args) {
        String message = "Hello, World!";
        System.out.println(message);
    }
}"""
        r = requests.post(f"{BASE}/analyze", json={"code": code, "language": "java"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["is_bug"], f"Clean Java code wrongly flagged as bug: {r.json()}")

    def test_clean_python(self):
        code = """
def add_numbers(a, b):
    return a + b
result = add_numbers(3, 4)
print(result)
"""
        r = requests.post(f"{BASE}/analyze", json={"code": code, "language": "python"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.json()["is_bug"], f"Clean Python code wrongly flagged as bug: {r.json()}")


class TestBuggyCode(unittest.TestCase):
    def test_null_pointer_java(self):
        code = """
public class Test {
    public static void main(String[] args) {
        String s = null;
        int n = s.length();
    }
}"""
        r = requests.post(f"{BASE}/analyze", json={"code": code, "language": "java"})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["is_bug"], f"Null pointer bug not detected: {data}")
        self.assertIn(
            "null",
            data["bug_type"].lower(),
            f"Expected 'null' in bug_type, got: {data['bug_type']!r}",
        )

    def test_python_index_error(self):
        code = """
items = [1, 2, 3]
last = items[len(items)]
print(last)
"""
        r = requests.post(f"{BASE}/analyze", json={"code": code, "language": "python"})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["is_bug"], f"Index-out-of-bounds bug not detected: {r.json()}")


class TestCorrectedCodeIsClean(unittest.TestCase):
    def test_fix_is_clean(self):
        """Submitting the suggested fix must return is_bug=False."""
        buggy_code = """
public class Test {
    public static void main(String[] args) {
        String s = null;
        int n = s.length();
    }
}"""
        # Step 1: get the fix
        r1 = requests.post(f"{BASE}/analyze", json={"code": buggy_code, "language": "java"})
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertTrue(data1["is_bug"], "First call should detect a bug")
        fixed_code = data1["fixed_code"]

        # Step 2: submit the fix — must return clean
        r2 = requests.post(f"{BASE}/analyze", json={"code": fixed_code, "language": "java"})
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertFalse(
            data2["is_bug"],
            f"Submitting the suggested fix returned is_bug=True. Bug NOT fixed.\nFix was:\n{fixed_code[:200]}",
        )


class TestValidation(unittest.TestCase):
    def test_empty_code(self):
        r = requests.post(f"{BASE}/analyze", json={"code": "", "language": "java"})
        self.assertEqual(
            r.status_code, 400,
            f"Expected 400 for empty code, got {r.status_code}: {r.text}",
        )

    def test_invalid_language(self):
        r = requests.post(f"{BASE}/analyze", json={"code": "x = 1", "language": "cobol"})
        self.assertEqual(
            r.status_code, 400,
            f"Expected 400 for unsupported language, got {r.status_code}: {r.text}",
        )

    def test_code_too_long(self):
        r = requests.post(f"{BASE}/analyze", json={"code": "x" * 10001, "language": "python"})
        self.assertEqual(
            r.status_code, 400,
            f"Expected 400 for oversized code, got {r.status_code}: {r.text}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
