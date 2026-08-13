#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


GENDER_MAP = {"female": "女性", "male": "男性"}


def load_payload(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if "data" in raw and isinstance(raw["data"], dict):
        return raw["data"]
    return raw


def load_array(data: dict, key: str) -> list[dict]:
    value = data.get(key, "[]")
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    return json.loads(value)


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def tgi_map(data: dict, key: str) -> dict:
    return {item.get("name"): item.get("value") for item in load_array(data, key)}


def fmt_pairs(data: dict, key: str, tgi_key: str | None = None, limit: int | None = None, name_map: dict | None = None) -> str:
    rows = load_array(data, key)
    if limit:
        rows = rows[:limit]
    tgis = tgi_map(data, tgi_key) if tgi_key else {}
    parts = []
    for row in rows:
        raw_name = row.get("name", "")
        name = name_map.get(raw_name, raw_name) if name_map else raw_name
        item = f"{name} {pct(float(row.get('value', 0)))}"
        if raw_name in tgis and tgis[raw_name] is not None:
            item += f" TGI{float(tgis[raw_name]):.2f}"
        parts.append(item)
    return "；".join(parts)


def fmt_tgi_only(data: dict, key: str, name_map: dict | None = None) -> str:
    parts = []
    for row in load_array(data, key):
        raw_name = row.get("name", "")
        name = name_map.get(raw_name, raw_name) if name_map else raw_name
        parts.append(f"{name} TGI{float(row.get('value', 0)):.2f}")
    return "；".join(parts)


def build_fields(data: dict, douyin_id: str, source_note: str) -> dict:
    return {
        "指数页粉丝分析抓取状态": "已抓取",
        "指数页粉丝分析-年龄占比": fmt_pairs(data, "Age"),
        "指数页粉丝分析-年龄TGI": fmt_tgi_only(data, "Age_Tgi"),
        "指数页粉丝分析-性别占比": fmt_pairs(data, "Gender", name_map=GENDER_MAP),
        "指数页粉丝分析-性别TGI": fmt_tgi_only(data, "Gender_Tgi", name_map=GENDER_MAP),
        "指数页粉丝分析-城市级别占比": fmt_pairs(data, "CityLabel", "CityLabel_Tgi"),
        "指数页粉丝分析-省份Top10": fmt_pairs(data, "Province", "Province_Tgi", limit=10),
        "指数页粉丝分析-城市Top20": fmt_pairs(data, "City", "City_Tgi", limit=20),
        "指数页粉丝分析-手机品牌Top5": fmt_pairs(data, "DeviceBrand", "DeviceBrand_Tgi", limit=5),
        "指数页粉丝分析-手机价格Top5": fmt_pairs(data, "DevicePrice", "DevicePrice_Tgi", limit=5),
        "指数页粉丝分析-来源备注": source_note,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Format Douyin get_great_user_fans_info response into workbook-ready fields.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--douyin-id", default="")
    parser.add_argument("--source-note", default="")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    data = load_payload(args.input)
    source_note = args.source_note or "抖音创作者中心-抖音指数-达人详情-粉丝分析；通过登录态页面 CDP 监听业务接口 /api/v2/daren/get_great_user_fans_info 读取返回比例"
    result = {
        "creator_douyin_id": args.douyin_id,
        "fields": build_fields(data, args.douyin_id, source_note),
        "raw_arrays": {
            key: load_array(data, key)
            for key in [
                "Age",
                "Age_Tgi",
                "Gender",
                "Gender_Tgi",
                "CityLabel",
                "CityLabel_Tgi",
                "Province",
                "Province_Tgi",
                "City",
                "City_Tgi",
                "DeviceBrand",
                "DeviceBrand_Tgi",
                "DevicePrice",
                "DevicePrice_Tgi",
            ]
            if key in data
        },
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
