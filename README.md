# おさかなキーボード  
これは、[おさかなキーボード](https://o24.works/fish/)のためのZMK Firmareの設定リポジトリです。  
キーマップを書き換えておさかなを更新する手順は[ユーザーガイド](https://o24.works/fish/guide/)を参照してください。  
  
## 書き換えていいファイル  
### [fish.keymap](config/boards/shields/fish/fish.keymap)  
キーの割り当てや入力の内容を設定できます。このファイルを視覚的に編集できる[キーマップエディター](https://o24.works/fish/editor/)も活用してください。  
### [fish.conf](config/boards/shields/fish/fish.conf)  
スリープ時間、検出名など、キーボード本体の挙動を設定できます。  
### [Kconfig.defconfig](config/boards/shields/fish/Kconfig.defconfig)
親機の左右を変えることができます。  

## Run GitHub Actions locally
GitHub CI builds firmware through `.github/workflows/build.yml`, which calls ZMK's reusable user-config workflow. Local runs use `.github/workflows/local-build.yml`, which mirrors the same `build.yaml` entries in the ZMK build container and writes firmware files directly to disk.

Prerequisites:

- Docker with access to the Docker daemon.
- Go, if `act` is not already installed.

Run the same workflow locally:

```sh
./scripts/run-github-actions-local
```

The script installs `act` v0.2.88 into `.local/bin` when no `act` binary is available, then runs the local workflow with the settings from `.actrc`. Local tool caches and firmware artifacts are written under `.local/`, which is ignored by git. Built firmware files are placed in `.local/firmware/`.
