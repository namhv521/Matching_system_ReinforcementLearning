# Hướng Dẫn PyTorch Từ Cơ Bản Đến Nâng Cao

## 1. PyTorch là gì?

PyTorch là một thư viện deep learning viết bằng Python, mặc định chạy trên CPU nhưng có thể tăng tốc bằng GPU thông qua CUDA. Điểm đặc trưng của PyTorch là cách tiếp cận "define-by-run" — đồ thị tính toán (computation graph) được xây dựng động ngay trong lúc chạy code, thay vì phải định nghĩa trước toàn bộ đồ thị. Nhờ vậy việc debug và tùy biến mô hình trở nên dễ dàng hơn nhiều so với cách tiếp cận đồ thị tĩnh truyền thống.

Ba đặc điểm nổi bật:
- Đồ thị tính toán động (dynamic computation graph) → linh hoạt khi thiết kế mô hình
- Tự động tính đạo hàm (automatic differentiation) qua module `autograd`
- Hỗ trợ tăng tốc GPU thông qua CUDA

### Cài đặt

Cài trên máy (Windows/macOS/Linux), chỉ dùng CPU:
```bash
pip install torch torchvision torchaudio
```

Cài trong notebook (Jupyter/Google Colab):
```bash
!pip install torch torchvision torchaudio
```

---

## 2. Tensor trong PyTorch

Tensor là cấu trúc dữ liệu nền tảng của PyTorch — về bản chất tương tự mảng NumPy, nhưng có thể chạy trên GPU và hỗ trợ tính đạo hàm tự động, nên rất phù hợp cho các tác vụ deep learning.

```python
import torch

# Tensor 1 chiều
x = torch.tensor([1.0, 2.0, 3.0])
print("Tensor 1D:", x)

# Tensor 2 chiều toàn số 0
y = torch.zeros((3, 3))
print("Tensor 2D:", y)
```

### Các phép toán cơ bản trên tensor

```python
a = torch.tensor([1.0, 2.0])
b = torch.tensor([3.0, 4.0])

# Cộng từng phần tử
print("Cộng theo từng phần tử:", a + b)

# Nhân ma trận
print("Nhân ma trận:", torch.matmul(a.view(2, 1), b.view(1, 2)))
```

### Reshape và Transpose

`reshape()` và `view()` đều dùng để thay đổi hình dạng (shape) của tensor mà không làm thay đổi dữ liệu bên trong. Khác biệt: `view()` yêu cầu dữ liệu tensor phải liên tục trong bộ nhớ (contiguous), còn `reshape()` linh hoạt hơn — nó sẽ tự tạo bản sao khi cần thiết để xử lý được nhiều trường hợp hơn.

```python
t = torch.tensor([[1, 2, 3, 4],
                   [5, 6, 7, 8],
                   [9, 10, 11, 12]])

print("Reshape thành (6, 2):")
print(t.reshape(6, 2))

print("Transpose (đổi chiều hàng-cột):")
print(t.transpose(0, 1))
```

---

## 3. Autograd và đồ thị tính toán

Module `autograd` tự động tính gradient phục vụ cho quá trình lan truyền ngược (backpropagation) — đây là bước then chốt khi huấn luyện mạng neural.

```python
x = torch.tensor(2.0, requires_grad=True)
y = x ** 2
y.backward()
print(x.grad)   # kết quả: tensor(4.)
```

Giải thích từng bước:
- `y = x ** 2`: PyTorch ghi lại phép toán này vào đồ thị tính toán.
- `y.backward()`: thực hiện lan truyền ngược, tính đạo hàm của `y` theo `x`.
- Vì `y = x²` nên `dy/dx = 2x`.
- Với `x = 2`, gradient bằng `2 × 2 = 4`, được lưu vào `x.grad`.

Nói cách khác, mỗi khi bạn thực hiện phép toán trên tensor có `requires_grad=True`, PyTorch sẽ tự dựng một đồ thị ghi nhớ toàn bộ các bước tính toán, để khi gọi `.backward()` nó có thể lần ngược lại và tính gradient cho từng biến.

---

## 4. Xây dựng mạng neural với `torch.nn`

Trong PyTorch, một mạng neural được xây dựng bằng cách kế thừa từ lớp `torch.nn.Module`, trong đó:

- `nn.Linear(in_features, out_features)`: định nghĩa một lớp fully-connected (dense).
- Các hàm kích hoạt như `torch.relu`, `torch.sigmoid`, `torch.softmax` được áp dụng giữa các lớp.
- Phương thức `forward()` quy định luồng dữ liệu đi qua mạng như thế nào.

```python
import torch
import torch.nn as nn

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(10, 16)
        self.fc2 = nn.Linear(16, 8)
        self.fc3 = nn.Linear(8, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.sigmoid(self.fc3(x))
        return x

model = NeuralNetwork()
print(model)
```

### Loss function và Optimizer

Sau khi định nghĩa mô hình, ta cần chọn:
- Một **hàm mất mát (loss function)** để đo lường sai số giữa dự đoán và nhãn thật.
- Một **optimizer** để cập nhật trọng số dựa trên gradient đã tính được.

Ví dụ: dùng `nn.BCELoss()` (binary cross-entropy) cho bài toán phân loại nhị phân, và `optim.Adam()` — kết hợp ưu điểm của momentum và learning rate thích ứng.

```python
model = NeuralNetwork()
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
```

### Vòng lặp huấn luyện (training loop)

Tạo dữ liệu giả (100 mẫu, mỗi mẫu 10 đặc trưng) rồi huấn luyện qua nhiều epoch. Mỗi vòng lặp gồm 5 bước cố định:

1. `optimizer.zero_grad()` — xóa gradient tích lũy từ bước trước.
2. `model(inputs)` — forward pass, tính dự đoán.
3. `criterion(outputs, targets)` — tính loss.
4. `loss.backward()` — lan truyền ngược, tính gradient cho toàn bộ trọng số.
5. `optimizer.step()` — cập nhật trọng số dựa trên gradient.

```python
inputs = torch.randn((100, 10))
targets = torch.randint(0, 2, (100, 1)).float()
epochs = 20

for epoch in range(epochs):
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(outputs, targets)
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 5 == 0:
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
```

---

## 5. PyTorch so với TensorFlow

| Tiêu chí | PyTorch | TensorFlow |
|---|---|---|
| Đồ thị tính toán | Động (dynamic) | Động theo mặc định (eager execution) |
| Độ dễ sử dụng | Rất "Pythonic", dễ debug | Đường học hơi dốc hơn |
| Hiệu năng | Nhanh nhờ eager execution | Tối ưu tốt cho triển khai quy mô lớn |
| Triển khai | TorchScript & ONNX | TensorFlow Serving & TensorFlow Lite |
| Mức phổ biến | Rất phổ biến trong nghiên cứu | Phổ biến, thiên về production |

## 6. Ứng dụng thực tế

- **Thị giác máy tính**: phân loại ảnh, phát hiện vật thể, phân đoạn ảnh — dùng CNN và Transformer (ví dụ ViT).
- **Xử lý ngôn ngữ tự nhiên**: hỗ trợ Transformer, RNN, LSTM cho sinh văn bản, phân tích cảm xúc...
- **Học tăng cường**: dùng trong DQN, Policy Gradient, Actor-Critic.

---

## 7. Bài tập thực hành cơ bản

1. Tạo một tensor 1 chiều gồm 5 số bất kỳ, sau đó tạo một tensor 2D kích thước (4,4) toàn số 1. In ra dtype và shape của cả hai.
2. Cho hai tensor `a = [2, 4, 6]` và `b = [1, 3, 5]`. Tính: cộng, trừ, nhân từng phần tử, và tích vô hướng (dot product) của chúng.
3. Tạo tensor kích thước (2, 6) chứa các số từ 1 đến 12, sau đó dùng `reshape()` để đưa về (3, 4), rồi `transpose()` để đổi thành (4, 3). In kết quả từng bước.
4. Cho `x = torch.tensor(3.0, requires_grad=True)` và `y = 2*x**3 + 5*x`. Tính `y.backward()` và giải thích bằng tay tại sao `x.grad` lại ra giá trị đó (gợi ý: đạo hàm là `6x² + 5`).
5. Viết một mạng neural đơn giản có 2 lớp ẩn, nhận đầu vào 4 đặc trưng, đầu ra là 3 lớp (dùng `softmax` ở lớp cuối cho bài toán phân loại đa lớp).
6. Viết vòng lặp huấn luyện hoàn chỉnh (data giả, loss, optimizer) cho mạng ở câu 5, chạy 10 epoch và in loss mỗi 2 epoch.

---

## 8. Lý thuyết nâng cao

### 8.1. Dataset và DataLoader

Khi làm việc với dữ liệu thật (không phải data giả `torch.randn`), PyTorch cung cấp hai lớp quan trọng: `torch.utils.data.Dataset` để đóng gói dữ liệu, và `DataLoader` để chia dữ liệu thành các batch, tự động shuffle và load song song bằng nhiều luồng.

```python
from torch.utils.data import Dataset, DataLoader

class MyDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

dataset = MyDataset(inputs, targets)
loader = DataLoader(dataset, batch_size=16, shuffle=True)
```

### 8.2. Chạy trên GPU (CUDA)

Để tận dụng GPU, cần chuyển cả model lẫn dữ liệu sang device tương ứng:

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
inputs, targets = inputs.to(device), targets.to(device)
```

Trên Google Colab, chỉ cần bật GPU runtime (Runtime → Change runtime type → GPU) là dòng code trên sẽ tự nhận diện và dùng GPU.

### 8.3. Mạng tích chập (CNN) với `torch.nn`

Với dữ liệu ảnh, thay vì chỉ dùng `nn.Linear`, ta dùng thêm `nn.Conv2d`, `nn.MaxPool2d`:

```python
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc = nn.Linear(16 * 16 * 16, 10)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = x.view(x.size(0), -1)  # flatten
        x = self.fc(x)
        return x
```

### 8.4. Learning rate scheduler

Thay vì giữ learning rate cố định, ta có thể giảm dần nó theo epoch để mô hình hội tụ ổn định hơn:

```python
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

for epoch in range(epochs):
    # ... training loop như trên ...
    scheduler.step()
```

### 8.5. Regularization: Dropout và BatchNorm

- `nn.Dropout(p=0.5)`: ngẫu nhiên "tắt" một số neuron trong lúc huấn luyện để chống overfitting.
- `nn.BatchNorm1d` / `nn.BatchNorm2d`: chuẩn hóa đầu ra của mỗi lớp, giúp huấn luyện nhanh và ổn định hơn.

```python
self.fc1 = nn.Linear(10, 32)
self.bn1 = nn.BatchNorm1d(32)
self.dropout = nn.Dropout(0.3)
# forward: x = self.dropout(torch.relu(self.bn1(self.fc1(x))))
```

### 8.6. Lưu và load mô hình

```python
# Lưu
torch.save(model.state_dict(), "model.pth")

# Load lại
model2 = NeuralNetwork()
model2.load_state_dict(torch.load("model.pth"))
model2.eval()  # chuyển sang chế độ đánh giá (tắt dropout, batchnorm dùng running stats)
```

### 8.7. Chế độ train() và eval()

`model.train()` bật lại dropout/batchnorm ở chế độ huấn luyện, còn `model.eval()` chuyển sang chế độ suy luận. Luôn nhớ gọi `model.eval()` trước khi đánh giá hoặc dự đoán, và bọc trong `with torch.no_grad():` để tiết kiệm bộ nhớ vì không cần tính gradient.

```python
model.eval()
with torch.no_grad():
    predictions = model(test_inputs)
```

---

## 9. Bài tập nâng cao

1. Viết một class `Dataset` tùy chỉnh nhận vào một mảng NumPy features/labels bất kỳ, kết hợp với `DataLoader` (batch_size=32, shuffle=True), rồi lặp qua toàn bộ loader và in shape của mỗi batch.
2. Viết lại vòng lặp huấn luyện ở bài tập cơ bản câu 6, nhưng sử dụng `DataLoader` thay vì đưa toàn bộ dữ liệu vào cùng lúc, đồng thời thêm đoạn code tự động chọn `cuda` nếu có GPU.
3. Xây dựng một `SimpleCNN` nhận đầu vào ảnh giả kích thước (batch, 3, 32, 32) (dùng `torch.randn`), thêm 2 lớp `Conv2d` + `MaxPool2d`, in ra shape sau mỗi lớp để hiểu cách kích thước ảnh thay đổi.
4. Thêm `nn.Dropout(0.3)` và `nn.BatchNorm1d` vào mạng ở bài tập cơ bản câu 5, huấn luyện và so sánh loss cuối cùng với phiên bản không có regularization.
5. Thêm `StepLR` scheduler vào vòng lặp huấn luyện, in ra learning rate hiện tại (`optimizer.param_groups[0]['lr']`) sau mỗi 5 epoch để quan sát nó giảm dần.
6. Huấn luyện xong một mô hình bất kỳ ở trên, lưu lại bằng `torch.save`, sau đó viết đoạn code load lại mô hình vào một instance mới và dùng nó để dự đoán trên dữ liệu test giả — nhớ đặt đúng `model.eval()` và `torch.no_grad()`.

---

*Gợi ý: bạn nên chạy thử từng đoạn code trên Google Colab (có GPU miễn phí) để vừa học vừa quan sát kết quả thực tế, đặc biệt hữu ích khi làm các bài tập về CNN và GPU.*
