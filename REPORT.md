# Bài thực hành Day 26 — Function Calling và MCP

- Họ tên: Đinh Đức Long
- MSSV: 2A202602633
- Ngày chạy: 14/10/2026 
- Môi trường: Windows PowerShell; Python 3.12 cho bước 01–03; môi trường riêng do uv quản lý cho Lab 04.
- Model thực tế: `gemini-3.5-flash`.

## Kết quả và bằng chứng

| Phần | Kết quả thực tế | Ảnh |
|---|---|---|
| 01 — Function Calling | Gemini yêu cầu `get_weather` cho Hà Nội và Đà Nẵng; app chạy hàm, gửi kết quả lại và nhận câu trả lời cuối. Exit code 0. | [01-function-calling.png](screenshots/01-function-calling.png) |
| 02 — MCP stdio | `list_tools` công bố `get_weather`; gọi thành công Hanoi, Danang, Haiphong. Exit code 0. | [02-mcp-client.png](screenshots/02-mcp-client.png) |
| 03a — Token đúng | Khám phá được tool và nhận kết quả thời tiết Hanoi. Exit code 0. | [03a-auth-ok.png](screenshots/03a-auth-ok.png) |
| 03a — Token sai | Client bị từ chối. Yêu cầu POST kiểm chứng độc lập nhận HTTP 401, `invalid_token`. Đây là kết quả mong đợi của phép thử âm. | [03a-auth-fail.png](screenshots/03a-auth-fail.png) |
| 03b — Registry | Tìm thấy 2 tool có tag `weather`; chọn `get_weather_v2` v2.0.0 và gọi thành công. | [03b-registry.png](screenshots/03b-registry.png) |
| 03c — Versioning | Đọc metadata, nhận thông báo deprecated; gọi được v1 dạng chuỗi và v2 JSON có `api_version: 2.0`, kèm forecast. | [03c-versioning.png](screenshots/03c-versioning.png) |
| 04 — Verify setup | Đủ dependency, import agent và server cổng 8085 phản hồi; `All checks passed!`. | [04-verify-setup.png](screenshots/04-verify-setup.png) |
| 04 — ADK current | Có sự kiện `get_current_weather("Hanoi")` và câu trả lời từ dữ liệu WeatherAPI thật. | [04-adk-current.png](screenshots/04-adk-current.png) |
| 04 — ADK forecast | Có sự kiện `get_forecast(city="Tokyo", days=3)` và bảng dự báo đủ 3 ngày. | [04-adk-forecast.png](screenshots/04-adk-forecast.png) |

Hai ảnh ADK chụp trực tiếp giao diện `adk web`. Bảy ảnh output chụp từ trang hiển thị bản ghi stdout/stderr của các lệnh đã chạy, **không phải cửa sổ terminal**. Bản ghi nguyên văn, lệnh, thời gian và exit code được lưu ở [screenshots/logs](screenshots/logs/). Không tạo câu trả lời hay dữ liệu giả để làm bằng chứng. Nếu yêu cầu chấm bài chỉ chấp nhận ảnh cửa sổ terminal, cần chạy lại các lệnh dưới đây và chụp terminal tương ứng.

Các sự kiện ADK được xuất từ session API để đối chiếu:

- [04-adk-current.json](screenshots/logs/04-adk-current.json): lời gọi tool, kết quả tool và câu trả lời cuối.
- [04-adk-forecast.json](screenshots/logs/04-adk-forecast.json): tham số `days=3`, ba ngày dự báo và câu trả lời cuối.

### Dữ liệu WeatherAPI trong lần chạy

Hà Nội: nhiệt độ **32.9°C**, cảm giác như **35.4°C**, độ ẩm **47%**, gió **3.6 km/h**, UV **6.9**, tầm nhìn **10 km**. Thời điểm cập nhật: **11:45, 14/10/2026**.

| Ngày ở Tokyo | Cao / thấp | Điều kiện | Khả năng mưa |
|---|---|---|---|
| 14/10/2026 | 28.5°C / 20.7°C | Nắng | 57% |
| 15/10/2026 | 21.8°C / 18.5°C | Có mây rải rác | 7% |
| 16/10/2026 | 25.0°C / 19.5°C | U ám | 13% |

Đây là dữ liệu tại thời điểm chạy; chạy lại sẽ có thể cho kết quả khác.

## Những điểm rút ra từ code

1. **Function Calling**: model chỉ trả tên hàm và tham số. Dòng `result = get_weather(**fc.args)` trong app mới thực thi hàm. Vòng `while resp.function_calls` gửi kết quả trở lại model.
2. **MCP**: server công bố schema từ `@mcp.tool()`, type hint và docstring. Client dùng `list_tools()` rồi `call_tool()`. Demo stdio không cần LLM và không cần key.
3. **Production demo**: bearer token được kiểm tra ở transport HTTP; registry chọn tool theo tag và phiên bản; giữ tool v1 bên cạnh v2 để client cũ vẫn hoạt động.
4. **ADK**: đảm nhiệm MCP client và vòng Function Calling. Agent nối đến `http://localhost:8085/mcp`; server mới giữ WeatherAPI key và gọi REST của WeatherAPI.
5. Dòng `All checks passed` chỉ là kiểm tra cấu hình; bằng chứng gọi tool và dữ liệu thật ở hai phiên ADK mới xác nhận luồng hoàn chỉnh.

## Chạy lại trên Windows

Chạy từ thư mục gốc repo. Key nằm trong `.env` cục bộ, được Git bỏ qua; không in nội dung file này khi chụp màn hình.

### Cài môi trường

```powershell
uv --cache-dir .uv-cache venv .venv --python 3.12
uv --cache-dir .uv-cache pip install --python .venv/Scripts/python.exe -r requirements.txt
Push-Location 04-lab/mcp-server
uv --cache-dir ../../.uv-cache sync --locked
Pop-Location
Push-Location 04-lab/mcp-client
uv --cache-dir ../../.uv-cache sync --locked
Pop-Location
```

### Bước 01–03

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:GEMINI_API_KEY = (Get-Content -LiteralPath .env | Where-Object { $_ -like 'GEMINI_API_KEY=*' }) -replace '^GEMINI_API_KEY=', ''
.venv/Scripts/python.exe 01-function-calling/weather_function_calling.py

Push-Location 02-mcp-basics
../.venv/Scripts/python.exe weather_client.py
Pop-Location

Push-Location 03-production
../.venv/Scripts/python.exe registry_client.py
../.venv/Scripts/python.exe versioned_client.py
Pop-Location
```

Auth cần hai terminal cùng đứng ở thư mục gốc repo:

```powershell
# Terminal 1
.venv/Scripts/python.exe 03-production/auth_server.py

# Terminal 2 — token mặc định của demo
.venv/Scripts/python.exe 03-production/auth_client.py

# Terminal 2 — phép thử token sai, lệnh thất bại là kết quả mong đợi
$env:MCP_AUTH_TOKEN = 'invalid-token-for-negative-test'
.venv/Scripts/python.exe 03-production/auth_client.py
Remove-Item Env:MCP_AUTH_TOKEN
```

Dừng auth server bằng Ctrl+C trước khi dùng ADK, vì cả hai dùng cổng 8000.

### WeatherAPI server và ADK

```powershell
# Terminal 1 — từ thư mục gốc
$env:WEATHERAPI_KEY = (Get-Content -LiteralPath .env | Where-Object { $_ -like 'WEATHERAPI_KEY=*' }) -replace '^WEATHERAPI_KEY=', ''
$env:PORT = '8085'
04-lab/mcp-server/.venv/Scripts/python.exe 04-lab/mcp-server/weather.py

# Terminal 2 — từ thư mục gốc
Set-Location 04-lab/mcp-client
.venv/Scripts/python.exe verify_setup.py
.venv/Scripts/adk.exe web --host 127.0.0.1 --port 8000
```

Client đọc `GOOGLE_API_KEY` và `MCP_SERVER_URL` từ `04-lab/mcp-client/.env` (UTF-8).
Mở [ADK web](http://localhost:8000), chọn `weather_agent`, hỏi thời tiết hiện tại và dự báo ba ngày.
Biến `PORT=8085` đảm bảo server dùng Streamable HTTP cả khi chạy từ tiến trình không có terminal tương tác.

### Kiểm thử thay đổi

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Hai test kiểm tra không in một phần API key và phục hồi khi Gemini trả HTTP 503 tạm thời. Cả hai đã qua.

