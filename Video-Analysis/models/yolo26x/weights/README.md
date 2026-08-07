# YOLO26x 权重

将 `yolo26x.pt` 放在本目录，并将上级 `model.yaml` 中的 `sha256` 更新为真实值：

```powershell
Get-FileHash .\Video-Analysis\models\yolo26x\weights\yolo26x.pt -Algorithm SHA256
```

实际权重文件默认不提交 Git。
