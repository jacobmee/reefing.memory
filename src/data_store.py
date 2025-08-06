from common import logger
import numpy as np
import json
import os
import requests
import uuid


def save_node_image(node_id, image_base64):
    """保存 base64 图片到 images 目录，返回图片路径"""
    if not image_base64:
        return None
    import base64
    image_data = image_base64.split(",", 1)[-1]
    image_bytes = base64.b64decode(image_data)
    
    image_dir = os.path.join(os.path.dirname(__file__), "static/images")
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, f"{node_id}.png")
    with open(image_path, "wb") as f:
        f.write(image_bytes)
    return f"static/images/{node_id}.png"


class ChartDataStore:
    def __init__(self):
        self.filename = os.path.join(os.path.dirname(__file__), "data", "data.json")

    def load_static_data(self):
        if not os.path.exists(self.filename):
            return {"labels": [], "values": []}
        with open(self.filename, "r") as f:
            data = json.load(f)
        # 限制最多返回25行（最后的）
        if isinstance(data, list):
            data = sorted(data, key=lambda d: d.get("time", ""))
            data = data[-20:]  # 取最后25行，顺序为从旧到新

        logger.debug("Loaded static  data:", data)
        return data

    def save_static_data(self, data):
        # Load existing data
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try:
                    all_data = json.load(f)
                except Exception:
                    all_data = []
        else:
            all_data = []
        # 查找是否有同日期记录
        found = False
        for idx, entry in enumerate(all_data):
            if entry.get("date") == data.get("date"):
                all_data[idx] = data
                found = True
                break
        if not found:
            all_data.append(data)
        # Save back
        with open(self.filename, "w") as f:
            json.dump(all_data, f, indent=2)

    def load_realtime_data(self, url="http://reef.lan:6001/data"):
        try:
            resp = requests.get(url, timeout=10)
            raw = resp.json()
            lines = raw.get("data", "").split("\n")
            cleaned = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    time = obj.get("time")
                    content = obj.get("content", "")
                    vals = {}
                    for entry in content.split("\n"):
                        entry = entry.strip()
                        if entry.startswith("ORP"):
                            vals["ORP"] = float(entry.split()[1])
                        elif entry.startswith("PH"):
                            vals["PH"] = float(entry.split()[1])
                        elif entry.startswith("T"):
                            vals["T"] = float(entry.split()[1])
                    if "ORP" in vals and "PH" in vals and "T" in vals:
                        cleaned.append(
                            {
                                "time": time,
                                "ORP": int(round(vals["ORP"])),
                                "PH": round(vals["PH"], 1),
                                "T": vals["T"],
                            }
                        )
                except Exception:
                    continue

            # 按小时分组（不做时间筛选）
            def get_hour(ts):
                return ts[:13] if ts else ""

            hour_map = {}
            for d in cleaned:
                hour = get_hour(d["time"])
                if hour not in hour_map:
                    hour_map[hour] = []
                hour_map[hour].append(d)

            filtered = []
            for hour, entries in hour_map.items():
                filtered.extend(entries)
            print(
                f"Filtered {len(cleaned)} entries to {len(filtered)} after hour grouping (no time limit)"
            )

            # 按时间倒序返回所有数据（不限制行数）
            filtered_sorted = sorted(filtered, key=lambda d: d["time"], reverse=True)
            print(
                f"Processed {len(filtered_sorted)} entries from real-time data after hour grouping"
            )

            # 如果没有数据，返回空列表
            if not filtered_sorted:
                return []

            return filtered_sorted
        except Exception as e:
            print(f"Error loading real-time data: {e}")
            return []


class StoryDataStore:
    def __init__(self, uuid=None):
        if uuid:
            self.data_path = os.path.join(os.path.dirname(__file__), "data", f"story_{uuid}.json")
        else:
            self.data_path = os.path.join(os.path.dirname(__file__), "data", "story.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {
            "header": {
                "main_title": "THE LOVE STORY",
                "subtitle": "A Journey Through Time for you or what you love",
            },
            "footer": {"footer_text": "© 2024 The love Company. All rights reserved."},
            "story_nodes": {},
        }

    def save_data(self, data):
        with open(self.data_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_story_nodes(self):
        data = self.load_data()
        return data.get("story_nodes", {})

    def set_story_nodes(self, nodes):
        for node_id, node in nodes.items():
            # 清理 image 字段中的 base64
            if (
                "image" in node
                and isinstance(node["image"], str)
                and node["image"].startswith("data:image/")
            ):
                node.pop("image")
            # 清理 avatar_image_base64/original_image_base64 等 base64 字段
            for k in list(node.keys()):
                if k.endswith("base64"):
                    node.pop(k)
        data = self.load_data()
        data["story_nodes"] = nodes
        self.save_data(data)

    def get_info(self):
        data = self.load_data()
        # Return header and footer info
        return {"header": data.get("header", {}), "footer": data.get("footer", {})}

    def set_info(self, info):
        data = self.load_data()
        data["header"] = info.get("header", {})
        data["footer"] = info.get("footer", {})
        self.save_data(data)

    def add_story_node(self, node_data):
        nodes = self.get_story_nodes()
        new_node_id = str(uuid.uuid4())
        node_data["id"] = new_node_id
        avatar_base64 = node_data.pop("avatar_image_base64", None)
        original_base64 = node_data.pop("original_image_base64", None)
        if avatar_base64:
            node_data["avatar_image"] = save_node_image(f"{new_node_id}_avatar", avatar_base64)
        if original_base64:
            node_data["original_image"] = save_node_image(f"{new_node_id}_original", original_base64)
        nodes[new_node_id] = node_data
        self.set_story_nodes(nodes)
        return node_data

    def update_story_node(self, node_id, updated_data):
        nodes = self.get_story_nodes()
        if node_id not in nodes:
            return None
        avatar_base64 = updated_data.pop("avatar_image_base64", None)
        original_base64 = updated_data.pop("original_image_base64", None)
        if avatar_base64:
            updated_data["avatar_image"] = save_node_image(f"{node_id}_avatar", avatar_base64)
        if original_base64:
            updated_data["original_image"] = save_node_image(f"{node_id}_original", original_base64)
        nodes[node_id].update(updated_data)
        self.set_story_nodes(nodes)
        return nodes[node_id]

    def delete_story_node(self, node_id):
        nodes = self.get_story_nodes()
        if node_id not in nodes:
            return False
        del nodes[node_id]
        self.set_story_nodes(nodes)
        return True

    def get_story_node(self, node_id):
        nodes = self.get_story_nodes()
        return nodes.get(node_id)


class SummaryDataStore:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "data", "summary.json")

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {
            "header": {
                "main_title": "THE LOVE STORY",
                "subtitle": "A Journey Through Time for you or what you love",
            },
            "footer": {"footer_text": "© 2024 The love Company. All rights reserved."},
            "summary_nodes": {},
        }

    def save_data(self, data):
        with open(self.data_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_summary_nodes(self):
        data = self.load_data()
        logger.debug(f"Summary nodes: {data.get('summary_nodes', {})}")
        return data.get("summary_nodes", {})

    def set_summary_order(self, order_list):
        """
        根据传入的节点 id 顺序列表，更新每个节点的 order 字段并保存。
        """
        if not isinstance(order_list, list):
            raise ValueError("order_list must be a list of node ids")
        nodes = self.get_summary_nodes()
        # 只更新存在的节点
        for idx, node_id in enumerate(order_list):
            if node_id in nodes:
                nodes[node_id]['order'] = idx
        self.set_summary_nodes(nodes)
        

    def set_summary_nodes(self, nodes):
        for node_id, node in nodes.items():
            # 清理 image 字段中的 base64
            if (
                "image" in node
                and isinstance(node["image"], str)
                and node["image"].startswith("data:image/")
            ):
                node.pop("image")
            # 清理 avatar_image_base64/original_image_base64 等 base64 字段
            for k in list(node.keys()):
                if k.endswith("base64"):
                    node.pop(k)
        # 按 order 排序 nodes
        sorted_items = sorted(
            nodes.items(),
            key=lambda x: x[1].get("order", 99999)
        )
        sorted_nodes = {k: v for k, v in sorted_items}
        data = self.load_data()
        data["summary_nodes"] = sorted_nodes
        self.save_data(data)

    def get_info(self):
        data = self.load_data()
        return {"header": data.get("header", {}), "footer": data.get("footer", {})}

    def set_info(self, info):
        data = self.load_data()
        data["header"] = info.get("header", {})
        data["footer"] = info.get("footer", {})
        self.save_data(data)

    def add_summary_node(self, node_data):
        nodes = self.get_summary_nodes()
        new_node_id = str(uuid.uuid4())
        node_data["id"] = new_node_id
        avatar_base64 = node_data.pop("avatar_image_base64", None)
        original_base64 = node_data.pop("original_image_base64", None)
        if avatar_base64:
            node_data["avatar_image"] = save_node_image(f"{new_node_id}_avatar", avatar_base64)
        if original_base64:
            node_data["original_image"] = save_node_image(f"{new_node_id}_original", original_base64)
        nodes[new_node_id] = node_data
        self.set_summary_nodes(nodes)
        return node_data

    def update_summary_node(self, node_id, updated_data):
        nodes = self.get_summary_nodes()
        if node_id not in nodes:
            return None
        avatar_base64 = updated_data.pop("avatar_image_base64", None)
        original_base64 = updated_data.pop("original_image_base64", None)
        if avatar_base64:
            updated_data["avatar_image"] = save_node_image(f"{node_id}_avatar", avatar_base64)
        if original_base64:
            updated_data["original_image"] = save_node_image(f"{node_id}_original", original_base64)
        nodes[node_id].update(updated_data)
        self.set_summary_nodes(nodes)
        return nodes[node_id]

    def delete_summary_node(self, node_id):
        nodes = self.get_summary_nodes()
        if node_id not in nodes:
            return False
        del nodes[node_id]
        self.set_summary_nodes(nodes)
        return True

    def get_summary_node(self, node_id):
        nodes = self.get_summary_nodes()
        return nodes.get(node_id)
