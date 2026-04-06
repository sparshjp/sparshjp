"""
Test file upload and URL crawling endpoints for AI Engine prompt box enhancement.
Tests: POST /api/agents/upload, POST /api/agents/crawl-url
"""
import pytest
import requests
import os
import tempfile

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestFileUpload:
    """Tests for POST /api/agents/upload endpoint"""
    
    def test_upload_text_file(self):
        """Upload a text file and verify response has id, filename, type='text', content"""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, this is a test text file.\nLine 2 of the file.\nLine 3 with some data.")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert 'id' in data, "Response should have 'id'"
            assert 'filename' in data, "Response should have 'filename'"
            assert 'type' in data, "Response should have 'type'"
            assert 'content' in data, "Response should have 'content'"
            
            # Verify values
            assert data['filename'] == 'test_document.txt', f"Expected filename 'test_document.txt', got {data['filename']}"
            assert data['type'] == 'text', f"Expected type 'text', got {data['type']}"
            assert 'Hello, this is a test text file' in data['content'], "Content should contain uploaded text"
            assert len(data['id']) > 0, "ID should not be empty"
            print(f"✓ Text file upload successful: id={data['id']}, type={data['type']}")
        finally:
            os.unlink(temp_path)
    
    def test_upload_csv_file(self):
        """Upload a CSV file and verify extraction works"""
        csv_content = "Name,Age,City\nAlice,30,New York\nBob,25,Los Angeles\nCharlie,35,Chicago"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('data.csv', f, 'text/csv')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
            data = response.json()
            
            # Verify response structure
            assert 'id' in data
            assert 'filename' in data
            assert 'type' in data
            assert 'content' in data
            
            # CSV should be extracted as document type
            assert data['type'] in ['document', 'text'], f"Expected type 'document' or 'text', got {data['type']}"
            assert data['filename'] == 'data.csv'
            
            # Verify CSV content was extracted (pipe-separated format)
            assert 'Alice' in data['content'], "Content should contain 'Alice'"
            assert 'Bob' in data['content'], "Content should contain 'Bob'"
            print(f"✓ CSV file upload successful: id={data['id']}, type={data['type']}")
        finally:
            os.unlink(temp_path)
    
    def test_upload_json_file(self):
        """Upload a JSON file and verify it's treated as text"""
        json_content = '{"name": "Test", "value": 123, "items": ["a", "b", "c"]}'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('config.json', f, 'application/json')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['type'] == 'text', f"JSON should be treated as text, got {data['type']}"
            assert '"name": "Test"' in data['content']
            print(f"✓ JSON file upload successful: id={data['id']}, type={data['type']}")
        finally:
            os.unlink(temp_path)
    
    def test_upload_python_file(self):
        """Upload a Python code file"""
        py_content = '''def hello_world():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello_world()
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(py_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('script.py', f, 'text/x-python')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['type'] == 'text'
            assert 'def hello_world' in data['content']
            print(f"✓ Python file upload successful: id={data['id']}, type={data['type']}")
        finally:
            os.unlink(temp_path)
    
    def test_upload_markdown_file(self):
        """Upload a Markdown file"""
        md_content = '''# Test Document

## Section 1
This is a test markdown file.

- Item 1
- Item 2
- Item 3

## Section 2
More content here.
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('readme.md', f, 'text/markdown')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['type'] == 'text'
            assert '# Test Document' in data['content']
            print(f"✓ Markdown file upload successful: id={data['id']}, type={data['type']}")
        finally:
            os.unlink(temp_path)


class TestURLCrawling:
    """Tests for POST /api/agents/crawl-url endpoint"""
    
    def test_crawl_valid_html_url(self):
        """Crawl https://httpbin.org/html and verify status=ok, type=html, content has text"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "https://httpbin.org/html"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'status' in data, "Response should have 'status'"
        assert 'url' in data, "Response should have 'url'"
        assert 'type' in data, "Response should have 'type'"
        assert 'content' in data, "Response should have 'content'"
        
        # Verify values
        assert data['status'] == 'ok', f"Expected status 'ok', got {data['status']}"
        assert data['type'] == 'html', f"Expected type 'html', got {data['type']}"
        assert len(data['content']) > 0, "Content should not be empty"
        
        # httpbin.org/html returns Herman Melville's Moby Dick excerpt
        assert 'Moby' in data['content'] or 'Herman' in data['content'] or len(data['content']) > 100, \
            "Content should contain text from the HTML page"
        
        print(f"✓ URL crawl successful: status={data['status']}, type={data['type']}, content_length={len(data['content'])}")
    
    def test_crawl_json_url(self):
        """Crawl a JSON endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "https://httpbin.org/json"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['status'] == 'ok'
        assert data['type'] == 'json'
        assert 'slideshow' in data['content'].lower() or len(data['content']) > 10
        print(f"✓ JSON URL crawl successful: type={data['type']}")
    
    def test_crawl_invalid_url_error_handling(self):
        """Crawl an invalid URL and verify error handling"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "https://this-domain-definitely-does-not-exist-12345.com/page"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200 (with error in body), got {response.status_code}"
        data = response.json()
        
        # Should return error status in the response body
        assert data['status'] == 'error', f"Expected status 'error' for invalid URL, got {data['status']}"
        assert 'error' in data, "Response should have 'error' field"
        assert len(data['error']) > 0, "Error message should not be empty"
        print(f"✓ Invalid URL error handling works: error={data['error'][:50]}...")
    
    def test_crawl_empty_url_returns_400(self):
        """Empty URL should return 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": ""},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400 for empty URL, got {response.status_code}"
        print(f"✓ Empty URL returns 400 as expected")
    
    def test_crawl_missing_url_returns_400(self):
        """Missing URL field should return 400 error"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400 for missing URL, got {response.status_code}"
        print(f"✓ Missing URL returns 400 as expected")
    
    def test_crawl_url_without_protocol(self):
        """URL without http/https should be auto-prefixed"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "httpbin.org/html"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should auto-prefix with https:// and work
        assert data['status'] == 'ok', f"Expected status 'ok', got {data['status']}"
        assert 'https://httpbin.org/html' in data['url']
        print(f"✓ URL auto-prefix works: {data['url']}")
    
    def test_crawl_url_returns_size(self):
        """Verify crawl response includes size_kb"""
        response = requests.post(
            f"{BASE_URL}/api/agents/crawl-url",
            json={"url": "https://httpbin.org/html"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'size_kb' in data, "Response should include size_kb"
        assert isinstance(data['size_kb'], (int, float)), "size_kb should be numeric"
        print(f"✓ URL crawl returns size: {data['size_kb']}KB")


class TestUploadEdgeCases:
    """Edge case tests for file upload"""
    
    def test_upload_empty_file(self):
        """Upload an empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('empty.txt', f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert 'id' in data
            assert data['content'] == '' or data['content'] is not None
            print(f"✓ Empty file upload handled: id={data['id']}")
        finally:
            os.unlink(temp_path)
    
    def test_upload_returns_ext(self):
        """Verify upload response includes file extension"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert 'ext' in data, "Response should include 'ext'"
            assert data['ext'] == '.txt', f"Expected ext '.txt', got {data['ext']}"
            print(f"✓ Upload returns extension: {data['ext']}")
        finally:
            os.unlink(temp_path)
    
    def test_upload_returns_size_kb(self):
        """Verify upload response includes size_kb"""
        content = "A" * 1024  # 1KB of content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                files = {'file': ('sized.txt', f, 'text/plain')}
                response = requests.post(f"{BASE_URL}/api/agents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert 'size_kb' in data, "Response should include 'size_kb'"
            assert data['size_kb'] >= 1.0, f"Expected size_kb >= 1.0, got {data['size_kb']}"
            print(f"✓ Upload returns size: {data['size_kb']}KB")
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
