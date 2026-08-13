---
name: douyin-creator-fans-analysis-capture
description: Capture Douyin Creator Center creator fan-analysis data for a known Douyin creator ID or creator-detail page, especially age, gender, province, city, city-level, device-brand, device-price ratios and TGI from 抖音创作者中心/抖音指数/达人详情/粉丝分析. Use when the user asks to抓取/核验/补充达人粉丝画像、粉丝分析、年龄段、性别占比、城市级别占比、城市分布、TGI, or to write these fields into an Excel creator workbook. Requires an authorized logged-in browser extension session; do not replace visible page navigation with unofficial bulk scraping.
---

# 抖音达人粉丝洞察抓取

Use this skill to extract fan-analysis ratios and TGI data from Douyin Creator Center's creator index page and write them into a creator workbook.

The target page flow is:

`抖音创作者中心 -> 抖音指数 -> 搜索达人抖音号 -> 达人详情 -> 粉丝分析`

Do not call this tab `粉丝画像`; the UI tab is `粉丝分析`.

## Guardrails

- Use the authorized logged-in browser extension session for Douyin pages. Follow the local browser instructions if present: create or reuse a dedicated task session/tab group, avoid the user's active tabs, and clean up intermediate tabs at the end.
- Stay inside visible, user-authorized page navigation. Searching one creator ID, opening that creator detail page, clicking `粉丝分析`, and reading that loaded page's own data is acceptable.
- Do not bulk-enumerate creators, guess endpoints across many IDs, bypass platform controls, or run high-speed background scraping.
- Prefer direct page-loaded data over screenshot interpretation. Use screenshots only as a fallback or visual audit.
- If a field is not exposed or a request body cannot be read, write `[待接口/页面数据重试]` rather than inventing values.
- Preserve existing workbook rows, including unsuitable creators and duplicates. Append new fields; do not delete or reorder existing candidate rows unless the user asks.

## Input Checklist

Collect or infer:

`达人抖音号 | 达人昵称 | 主页链接或指数页详情链接 | Excel 路径 | 写入范围 | 需要字段`

For the first workbook row, find `抖音号` from the workbook if the user says "第一个达人".

Recommended new Excel fields:

`指数页粉丝分析抓取状态 | 指数页达人昵称 | 指数页总粉丝量 | 指数页总获赞量 | 指数页总作品数 | 指数页粉丝分析-年龄占比 | 指数页粉丝分析-年龄TGI | 指数页粉丝分析-性别占比 | 指数页粉丝分析-性别TGI | 指数页粉丝分析-城市级别占比 | 指数页粉丝分析-省份Top10 | 指数页粉丝分析-城市Top20 | 指数页粉丝分析-手机品牌Top5 | 指数页粉丝分析-手机价格Top5 | 指数页粉丝分析-来源备注`

## Browser Workflow

1. Open the Creator Center index page in the logged-in extension browser:

   `https://creator.douyin.com/creator-micro/creator-count/arithmetic-index?type=3&source=creator`

2. Search by the creator's Douyin ID, not by a content keyword.

   The search box placeholder is usually:

   `请输入您想查询的达人名称或达人抖音号`

3. Verify the search result matches the expected creator nickname and Douyin ID. Click `达人详情`.

4. On detail page, wait until these fields load before moving on:

   `抖音号 | 总粉丝量 | 总获赞量 | 总作品数 | 作者分析 | 作品分析 | 粉丝分析`

5. Enable CDP network capture before triggering the fan-analysis request:

   - Use the tab capability `cdp`.
   - Send `Network.enable` with large enough buffers.
   - Read the current CDP event cursor.
   - Click `粉丝分析`.
   - If needed, click `城市级别`, `城市`, and `省份` to trigger regional views.
   - Read `Network.responseReceived` events after the cursor.

6. Look for this business endpoint in the loaded page's own network traffic:

   `/api/v2/daren/get_great_user_fans_info`

   The response body is JSON and usually contains stringified JSON arrays under:

   `Age | Age_Tgi | Gender | Gender_Tgi | Province | Province_Tgi | City | City_Tgi | CityLabel | CityLabel_Tgi | DeviceBrand | DeviceBrand_Tgi | DevicePrice | DevicePrice_Tgi`

7. If no fan-info request appears, reload the same detail page with network capture already enabled, wait for detail fields, then click `粉丝分析` again. Do not repeatedly query guessed endpoint variants.

## Parsing Rules

- Convert ratio values from decimals to percentages with two decimals:

  `0.313725... -> 31.37%`

- Keep TGI to two decimals:

  `140.0276 -> TGI140.03`

- Map gender keys:

  `female -> 女性`, `male -> 男性`

- Preserve the source order from each array unless the user asks for a different sort. The UI and endpoint often already return sorted share arrays.
- Pair ratio arrays with the same-name `_Tgi` array by `name`.
- Recommended workbook display limits:

  `省份Top10 | 城市Top20 | 手机品牌Top5 | 手机价格Top5`

- Store full raw and parsed JSON evidence when feasible:

  `verification/creator_index_get_great_user_fans_info_raw_<douyin_id>.json`

  `verification/creator_index_get_great_user_fans_info_parsed_<douyin_id>.json`

## Helper Script

Use `scripts/format_fans_info.py` to convert one captured `get_great_user_fans_info` response into Excel-ready fields.

Example:

```bash
python scripts/format_fans_info.py \
  --input verification/creator_index_get_great_user_fans_info_raw.json \
  --douyin-id 77165880495 \
  --source-note "抖音创作者中心-抖音指数-达人详情-粉丝分析；通过登录态页面 CDP 监听业务接口读取返回比例；2026-08-14" \
  --output verification/creator_index_get_great_user_fans_info_parsed.json
```

The script prints a JSON object with `fields` that can be written to Excel.

## Excel Writeback

When updating a workbook:

1. Create a timestamped backup before saving.
2. Append new columns if absent.
3. Locate all rows matching the Douyin ID; update duplicates too unless the user asks for only one row.
4. Do not overwrite complete prior creator verification fields unless the new value is the requested fan-analysis field.
5. Add a compact audit sheet such as `指数页粉丝分析_首个达人` or `指数页粉丝分析_抓取记录` when useful.
6. Keep row heights readable. Long ratio fields should wrap inside moderate-width columns; avoid making single rows extremely tall in the readable workbook.

Recommended source remark:

`抖音创作者中心-抖音指数-达人详情-粉丝分析；通过登录态页面 CDP 监听业务接口 /api/v2/daren/get_great_user_fans_info 读取返回比例；YYYY-MM-DD`

## Fallbacks

- If普通文本 DOM exposes table rows, it can be used as partial evidence. For example, province and gender may render as text while age and city-level ratios do not.
- If the endpoint cannot be captured after one reload and one tab-click retry, record the visible DOM values and mark hidden fields as `[待接口/页面数据重试]`.
- If screenshots are needed, save them only as audit evidence; do not treat visual estimates as exact percentages unless the user accepts screenshot-based approximation.
