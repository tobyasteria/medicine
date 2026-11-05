# KẾ HOẠCH DỰ ÁN — MEDICAL IMAGE CLASSIFICATION CHALLENGE 2026

*Bản v1.0 — 30/10/2026. Nguồn quy định: “Thể lệ Medical Image Classification Challenge 2026”, 6 trang, Ban Tổ chức cuộc thi.*

## 1. Mục tiêu, cách chấm và nguyên tắc hợp lệ

**Bài toán:** phân loại ảnh X-quang phổi thành `Normal` và `Pneumonia`. Chỉ sử dụng tập ảnh được Ban Tổ chức cung cấp, gồm `Train`, `Validation`, `Test` (Test **không** có nhãn). Toàn bộ huấn luyện và xử lý ảnh trên **Jupyter Notebook của Kaggle** bằng **Python** và thư viện được phép.

**Performance**: `P = 0.30*Accuracy + 0.25*Sensitivity + 0.20*Specificity + 0.25*F1`. Khi tính trong notebook, **Pneumonia là lớp dương (positive class)**. Cần xác nhận Ban Tổ chức cũng dùng đúng định nghĩa lớp dương, đặc biệt với F1.

**Sơ loại:** `Final Score = 0.90*Performance + 0.10*Technical`.

**Chung kết:** Performance 50%, Technical 20%, báo cáo + trình bày 15%, phản biện 15%.

**Technical** gồm: tiền xử lý hợp lý (2 điểm), augmentation (2), kiến trúc (2), phân tích kết quả (2), trình bày pipeline (2).

**Bài nộp:** một `.zip`, tối thiểu gồm: 1 file `.pkl`, 1 file `team01.csv` (thay bằng tên đội theo hướng dẫn nếu có) gồm **đúng hai cột** `Image_id,Prediction` với giá trị `Normal` / `Pneumonia`, và 1 file notebook `.ipynb`. CSV phải được sinh ra bằng cách **chạy tuần tự notebook từ trên xuống dưới**, không chỉnh sửa nhãn hoặc dữ liệu thủ công.

**Bắt buộc tránh:** dùng test labels; đưa ảnh y tế bên ngoài vào tập train; tải weights ngoài phạm vi cho phép; dùng model train trực tiếp trên test; trao đổi dataset/model giữa đội; sao chép nguồn đội khác; nộp kết quả không tái lập. AI/LLM được hỗ trợ tư duy/lập trình nhưng nhóm phải hiểu và bảo vệ được mã nguồn, trực tiếp thực hiện bài.

## 2. Kiến trúc sản phẩm chủ đạo

```text
[Organizer-provided Train/Validation/Test]
                  |
        [Dataset integrity audit]
             - split counts
             - class distribution
             - image quality
             - patient duplicate checks (if IDs available)
                  |
       [Training-only augmentation]         [Val/Test deterministic transforms]
       - mild rotation ±7°                     - resize 224
       - mild crop/brightness                  - 3-channel grayscale
       - normalise                             - normalise
                  |                                  |
        [CNN: ResNet18 scratch] ----------------------+
                  |
          [Weighted cross-entropy]
                  |
             [AdamW + cosine LR]
                  |
            [Best epoch by P@0.50]
                  |
         [Validation: Se/Sp/F1/CM]
                  |
       [Optional threshold validation]
                  |
          [Save self-contained model.pkl]
                  |
          [Reload .pkl and test sanity]
                  |
         [Test image files only, no labels]
                  |
     [Image_id, Prediction -> team01.csv]
```

**Vì sao chọn ResNet18 trước?** Đây là một baseline phổ biến, tương đối dễ chạy trên GPU Kaggle, đủ đơn giản để kiểm soát và giải thích. Không có bằng chứng rằng nó sẽ là mô hình thắng; cần đo trên validation thực tế. Trong notebook, `weights=None` để không tải weights từ mạng. Nếu BTC cho phép pretrained weights, sẽ mở nhánh thử nghiệm transfer learning **riêng biệt**, có ghi rõ nguồn và phạm vi cho phép.

**Vì sao ưu tiên Sensitivity và Specificity?** Accuracy một mình có thể che lấp lỗi bỏ sót Pneumonia khi hai lớp mất cân bằng. Mọi biểu đồ và báo cáo cần có ma trận nhầm lẫn (TP, TN, FP, FN) và điểm **P theo công thức chính thức**, không chọn mô hình dựa vào accuracy riêng lẻ.

## 3. Lộ trình đề xuất, tính từ ngày 30/10/2026

| Thời gian | Mục tiêu | Thành phẩm có thể kiểm chứng |
|---|---|---|
| 30/10 | Xác minh điều lệ, quyền tham gia, link dataset, cấu trúc file, GPU Kaggle | Nhật ký rule-check và danh sách file |
| 31/10–01/11 | Baseline chạy end-to-end; audit label/split | Notebook E00, confusion matrix, P/Se/Sp/F1 |
| 02–03/11 | Controlled experiments: augmentation, architecture, resize | E01–E03: so sánh có số liệu |
| 04–05/11 | Ablation CLAHE, cân bằng lớp, threshold nếu val đủ lớn | E04–E05, bảng lý giải cải thiện/suy giảm |
| 06/11 | Chốt model sơ loại, chạy notebook từ đầu, zip, thử khôi phục pkl | Bộ nộp hợp lệ, checklist PASS |
| 07/11 | Vòng sơ loại (theo lịch **dự kiến**) | Submission chính thức |
| 08–10/11 | Chỉ cải thiện dựa trên validation và thông báo BTC; chuẩn bị slide và Q&A | Báo cáo, hình pipeline, log thí nghiệm |
| 11/11 | Diễn tập trình bày và phản biện; kiểm tra chạy lại | Runbook chung kết |
| 12/11 | Chung kết (theo lịch **dự kiến**) | Bộ nộp và bảo vệ |

**Lưu ý thời hạn:** Quy định ghi đăng ký từ 09–16/10/2026, đã qua tại thời điểm lập kế hoạch. Lịch sơ loại/chung kết đều ghi **dự kiến**. Nếu đội chưa đăng ký, cần xác minh trực tiếp với BTC xem có được bổ sung hay không.

## 4. Quy trình thí nghiệm tránh overfitting / data leakage

1. Cố định `Train/Val/Test` do BTC cung cấp, tuyệt đối không sử dụng bất kỳ nhãn Test nào.
2. Kiểm tra số lượng hai lớp, tỷ lệ thiếu ảnh/hỏng ảnh, kích thước ảnh và ảnh trùng nếu có thể. Nếu có patient ID, kiểm tra overlap giữa train và validation, báo BTC khi phát hiện lỗi phân chia.
3. Tạo **E00 baseline** rồi lưu đầy đủ kết quả. Chỉ thay đổi một nhóm yếu tố chính trong mỗi experiment để biết nguyên nhân tăng/giảm điểm.
4. Chọn best epoch theo validation `P@0.50`. Đề xuất chọn ngưỡng dự đoán trên validation bằng một lưới nhỏ đã định trước; nếu validation mỗi lớp ít hơn 50 ảnh thì giữ 0.5.
5. Không nhìn điểm test ẩn để thay đổi quá nhiều lần. Mọi phương án ensemble chỉ làm khi có bằng chứng validation ổn định và kiểm thử pipeline đủ thời gian.
6. Chốt notebook và chạy hoàn chỉnh từ trên xuống dưới; CSV được tạo từ `.pkl` được load lại.

**Lưu ý:** Đánh giá lại quá nhiều lần trên một validation cố định cũng có thể làm kết quả val lạc quan. Nếu số lượng ảnh cho phép, sử dụng thêm CV *trong nội bộ Train* hoặc repeated seeds để đánh giá độ ổn định, không tạo thêm external data.

## 5. Sổ theo dõi thí nghiệm (điền số thật sau khi chạy)

| ID | Model / weights | Image | Augmentation | Class handling | Threshold | P | Se | Sp | F1 | Ghi chú |
|---|---|---:|---|---|---:|---:|---:|---:|---:|---|
| E00 | ResNet18 / scratch | 224 | nhẹ | weighted CE | 0.50 | TBD | TBD | TBD | TBD | baseline |
| E01 | ResNet18 / scratch | 224 | không | weighted CE | 0.50 | TBD | TBD | TBD | TBD | ablation augmentation |
| E02 | EfficientNet-B0 / scratch | 224 | nhẹ | weighted CE | 0.50 | TBD | TBD | TBD | TBD | so sánh model |
| E03 | ResNet18 / scratch | 288 hoặc 320 | nhẹ | weighted CE | 0.50 | TBD | TBD | TBD | TBD | giữ chi tiết |
| E04 | Model tốt nhất | 224–320 | + CLAHE | weighted CE | 0.50 | TBD | TBD | TBD | TBD | CLAHE train/val/test đồng nhất |
| E05 | Model tốt nhất | tối ưu | lựa chọn tốt nhất | theo đo lường | val-tuned | TBD | TBD | TBD | TBD | chọn ngưỡng |
| E06 | Ensemble (nếu hợp lệ) | tối ưu | lựa chọn tốt nhất | theo đo lường | val-tuned | TBD | TBD | TBD | TBD | tránh overfit |

`TBD` = chưa huấn luyện trên dữ liệu chính thức, **không phải số điểm thực**.

## 6. Kịch bản slide bảo vệ (6–8 trang)

- **Slide 1** — Nhiệm vụ, mục tiêu và ràng buộc dữ liệu.
- **Slide 2** — Số ảnh, tỷ lệ Normal/Pneumonia, nguy cơ lệch lớp/leakage và phân tích ảnh mẫu chính thức.
- **Slide 3** — Sơ đồ toàn bộ pipeline và chọn preprocessing.
- **Slide 4** — Kiến trúc mạng, loss/optimizer/learning rate, tài nguyên Kaggle.
- **Slide 5** — Ablation table: baseline so với cải tiến, giải thích vì sao loại/bổ sung mỗi kỹ thuật.
- **Slide 6** — Performance: P, Accuracy, Se, Sp, F1, confusion matrix, FP/FN và ví dụ lỗi validation.
- **Slide 7** — Kết quả tái lập, quy trình sinh .pkl + CSV, bằng chứng chạy từ trên xuống dưới.
- **Slide 8** — Hạn chế: nguy cơ domain shift, tính đại diện của ảnh, chưa chứng minh đủ điều kiện dùng trong y khoa.

## 7. Câu hỏi giám khảo thường có thể hỏi

**Q1. Tại sao Accuracy cao nhưng P thấp?** Vì P còn đánh trọng số Sensitivity, Specificity và F1; dự đoán thiên lệch về lớp phổ biến gây mất điểm.

**Q2. Positive class là gì?** Trong pipeline hiện tại: Pneumonia = 1. Cần đối chiếu với BTC về cách tính F1 chính thức.

**Q3. Tại sao không dùng Horizontal Flip?** Cấu trúc giải phẫu có tính trái/phải và ký hiệu ảnh; tác động của flip cần được kiểm chứng riêng, không mặc nhiên an toàn.

**Q4. Tại sao không bật CLAHE ngay từ đầu?** CLAHE có thể tăng tương phản nhưng cũng tăng noise/tạo artefact. Chỉ giữ nếu kết quả trên validation chứng minh có lợi.

**Q5. Tại sao pretrained weights=None?** Mục đích tuân thủ rõ ràng điều cấm tải mô hình ngoài phạm vi cho phép. Nếu BTC cho phép pretrained, có thể test có kiểm soát.

**Q6. Xử lý imbalance thế nào?** Bắt đầu bằng class-weighted cross-entropy. Không đồng thời oversample và weight loss mà không ablate, tránh điều chỉnh quá mức.

**Q7. Chứng minh reproducibility?** Ghi seed, package version, config; notebook chạy toàn bộ từ đầu; file `.pkl` lưu weights và preprocessing config; inference đọc lại `.pkl`; assertion kiểm tra nhất quán validation và định dạng CSV.

**Q8. Ngưỡng 0.5 có tối ưu không?** Không chắc. Có thể thử ngưỡng trên validation với phạm vi nhỏ, đồng thời tránh overfit khi val nhỏ.

**Q9. Có thể dùng ảnh X-ray trên Kaggle khác để train không?** Không. Chỉ dataset do BTC cung cấp.

**Q10. Mô hình có thể chẩn đoán bệnh nhân thật?** Không thể khẳng định từ điểm thi. Cần kiểm định ngoài miền dữ liệu, nghiên cứu lâm sàng và phê duyệt liên quan.

## 8. Checklist trước khi nộp

- [ ] Tên đội hợp lệ; quy định thời gian và pretrained weights đã xác minh với BTC.
- [ ] Không có ảnh ngoài dataset BTC; không truy cập nhãn test.
- [ ] Notebook chạy trong **Kaggle** với GPU (nếu dùng) và không `pip install` hoặc network download.
- [ ] `Run All` hoàn chỉnh, không hardcode kết quả test, không sửa CSV thủ công.
- [ ] `.pkl` load lại thành công; class mapping và ngưỡng giống lần sinh CSV.
- [ ] CSV đúng 2 cột `Image_id` và `Prediction`; số dòng bằng số ảnh test, không thiếu/trùng tên, nhãn chỉ `Normal` hoặc `Pneumonia`.
- [ ] `.zip` có tối thiểu `.pkl`, `.csv`, `.ipynb`, đúng quy ước BTC.
- [ ] Cả nhóm giải thích được augmentation, model, objective function, metrics, xử lý lỗi và quá trình training.

## 9. Những thông tin còn cần xác nhận từ BTC / dữ liệu thật

1. Dataset chính thức và cấu trúc file (folder theo lớp hay CSV label?).
2. BTC cho phép pretrained checkpoints nào, nếu có? Từ nguồn nào và có được gắn vào Kaggle notebook hay không?
3. Cách tính F1 trong bài chấm chính thức: positive = Pneumonia? Binary hay macro F1?
4. `team01.csv` là tên ví dụ hay bắt buộc; yêu cầu định dạng chính xác `.pkl` là gì (PyTorch state_dict trong pickle có được chấp nhận không?).
5. Có metadata patient ID để kiểm tra rò rỉ giữa train và validation không?
6. Giới hạn thời gian chạy, GPU quota, kích thước file zip và thời điểm nộp cụ thể.

---

**Trạng thái:** Notebook starter đã chạy thử end-to-end với **dữ liệu giả lập** và pass các phép kiểm tra lưu/đọc mô hình, định dạng CSV. Chưa huấn luyện hoặc đo điểm thực tế trên dữ liệu của Ban Tổ chức. Mọi điểm thực chỉ được báo cáo sau khi nhóm chạy trên dữ liệu đúng quy định.
