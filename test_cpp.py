import requests
code = "#include <iostream>
class Logger {
public:
    void log() {
        int* timestamp = new int(12345);
    }
};"
r = requests.post('http://127.0.0.1:5000/analyze', json={'code': code, 'language': 'cpp'})
print(r.json())