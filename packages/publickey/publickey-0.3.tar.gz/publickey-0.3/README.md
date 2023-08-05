# 機能概要

* YAMLに設定したユーザーの公開鍵をGithubからダウンロード
* YAMLに設定したホストにauthrized_keysファイルを配置
* YAMLの設定から~/.ssh/config 用ファイルを生成

## YAMLの例

sample.yml:
```
group:
  - &developers
    - oyakata        # Yakata Imagawa
    - feiz           # Kenta Azuma
  - &superusers
    - oyakata        # Yakata Imagawa


development.example.com:
  title: 開発環境
  hostname: 127.0.0.1
  members: *developers
  tags: development


example.com:
  title: 本番環境
  hostname: 127.0.0.1
  members: *superusers
  tags: production
```

### ~/.ssh/config を生成

    $ publickey config sample.yml -t production > ssh_config

生成された ssh_config:
```
Host example.com
  # 本番環境
  HostName 127.0.0.1
  Port 22
  User ubuntu
  IdentityFile ~/.ssh/id_rsa

ServerAliveInterval 120
```

### Githubの公開鍵を一括取得

    $ publickey get sample.yml development.example.com > authorized_keys  # oyakata, feizの鍵
    $ publickey get sample.yml example.com > authorized_keys  # oyakataの鍵のみ


### ファイルをホストに配置

    $ publickey put -s authorized_keys example.com  # ファイルを指定してput
    $ publickey put -e sample.yml example.com       # Githubの鍵をダウンロードしてput
