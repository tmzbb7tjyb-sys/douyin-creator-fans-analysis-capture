# 抖音达人粉丝洞察抓取

这是一个用于从抖音创作者中心的达人详情页抓取粉丝分析数据的 Codex skill。它面向已经知道达人抖音号、达人主页或指数页详情页的场景，用来补充年龄、性别、省份、城市、城市级别、手机品牌、手机价格等比例和 TGI 字段。

目标页面路径是：

```text
抖音创作者中心 -> 抖音指数 -> 搜索达人抖音号 -> 达人详情 -> 粉丝分析
```

注意：这里的 UI 标签叫 `粉丝分析`，不要写成 `粉丝画像`。

## 适用场景

- 抓取或核验单个达人粉丝分析。
- 给达人 Excel 表补充粉丝年龄、性别、地域、设备字段。
- 从抖音指数达人详情页读取总粉丝量、总获赞量、总作品数。
- 需要把接口返回 JSON 转成 Excel 可读字段。

## 不适用场景

- 不适合批量枚举达人、扫 ID 或绕过平台限制。
- 不适合用后台接口替代可见页面授权访问。
- 不适合凭截图估算精确比例，除非用户明确接受近似值。

## 平台访问边界

访问抖音页面时，必须使用已登录的授权浏览器扩展会话，并保持在可见页面流程内：

- 打开抖音创作者中心指数页。
- 搜索一个明确的达人抖音号。
- 校验搜索结果与预期达人匹配。
- 进入达人详情页。
- 点击 `粉丝分析`。
- 只读取该页面自身加载出的业务数据。

禁止批量枚举、猜接口变体、高速抓取、多 ID 后台请求或绕过登录页面的数据访问。

## 核心数据

优先从页面加载出的业务接口读取：

```text
/api/v2/daren/get_great_user_fans_info
```

常见字段包括：

```text
Age
Age_Tgi
Gender
Gender_Tgi
Province
Province_Tgi
City
City_Tgi
CityLabel
CityLabel_Tgi
DeviceBrand
DeviceBrand_Tgi
DevicePrice
DevicePrice_Tgi
```

如果接口或页面字段暂时不可读，应写 `[待接口/页面数据重试]`，不要编造。

## 输出字段

推荐写入 Excel 的字段：

```text
指数页粉丝分析抓取状态
指数页达人昵称
指数页总粉丝量
指数页总获赞量
指数页总作品数
指数页粉丝分析-年龄占比
指数页粉丝分析-年龄TGI
指数页粉丝分析-性别占比
指数页粉丝分析-性别TGI
指数页粉丝分析-城市级别占比
指数页粉丝分析-省份Top10
指数页粉丝分析-城市Top20
指数页粉丝分析-手机品牌Top5
指数页粉丝分析-手机价格Top5
指数页粉丝分析-来源备注
```

格式规则：

- 比例从小数转成百分比并保留两位，例如 `0.3137 -> 31.37%`。
- TGI 保留两位，例如 `140.0276 -> TGI140.03`。
- 性别字段映射为 `女性`、`男性`。
- 按接口数组原始顺序保留，除非用户要求另行排序。

## 辅助脚本

仓库包含 `scripts/format_fans_info.py`，可把捕获到的 `get_great_user_fans_info` JSON 转成 Excel 可写字段。

```bash
python scripts/format_fans_info.py \
  --input verification/creator_index_get_great_user_fans_info_raw.json \
  --douyin-id 77165880495 \
  --source-note "抖音创作者中心-抖音指数-达人详情-粉丝分析；通过登录态页面 CDP 监听业务接口读取返回比例；2026-08-14" \
  --output verification/creator_index_get_great_user_fans_info_parsed.json
```

脚本输出包含：

- `fields`：可写入 Excel 的格式化字段。
- `raw_arrays`：解析后的原始数组，便于复核。
- `creator_douyin_id`：当前达人抖音号。

## 安装

将仓库 clone 到 Codex skills 目录：

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/tmzbb7tjyb-sys/douyin-creator-fans-analysis-capture.git
```

然后在新的 Codex 任务中触发：

```text
用 $douyin-creator-fans-analysis-capture 抓取这个达人在抖音指数里的粉丝分析，并写回 Excel。
```

## 示例提示词

```text
用 $douyin-creator-fans-analysis-capture 抓取第一个达人粉丝分析。
Excel 在：/path/to/达人表.xlsx
请补充年龄、性别、城市级别、省份Top10、城市Top20、手机品牌Top5、手机价格Top5，并保留原始 JSON 证据。
```

## 目录结构

```text
.
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── format_fans_info.py
```

## 注意事项

- 详细执行规则以 [SKILL.md](SKILL.md) 为准。
- 写回 Excel 前应先创建时间戳备份。
- 重复达人行默认都要更新，除非用户指定只更新一行。
- 可见 DOM 数据可以作为 fallback，但隐藏比例和 TGI 不应凭视觉估算。
