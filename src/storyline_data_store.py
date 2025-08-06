import os
import json
import uuid

class StorylineDataStore:
    def __init__(self):
        self.data_path = os.path.join(os.path.dirname(__file__), 'data', 'story.json')

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                return json.load(f)
        return {
            "header": {
                "main_title": "THE LOVE STORY",
                "subtitle": "A Journey Through Time for you or what you love",
            },
            "footer": {
                "footer_text": "© 2024 The love Company. All rights reserved."
            },
            "storyline_nodes": {}
        }

    def save_data(self, data):
        with open(self.data_path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_storyline_nodes(self):
        data = self.load_data()
        return data.get('storyline_nodes', {})

    def set_storyline_nodes(self, nodes):
        for node_id, node in nodes.items():
            if 'image' in node and isinstance(node['image'], str) and node['image'].startswith('data:image/'):
                node.pop('image')
        data = self.load_data()
        data['storyline_nodes'] = nodes
        self.save_data(data)

    def get_header_footer(self):
        data = self.load_data()
        return {
            "header": data.get('header', {}),
            "footer": data.get('footer', {})
        }

    def set_header_footer(self, header_footer):
        data = self.load_data()
        data['header'] = header_footer.get('header', {})
        data['footer'] = header_footer.get('footer', {})
        self.save_data(data)

    def add_storyline_node(self, node_data):
        nodes = self.get_storyline_nodes()
        new_node_id = str(uuid.uuid4())
        node_data['id'] = new_node_id
        nodes[new_node_id] = node_data
        self.set_storyline_nodes(nodes)
        return node_data

    def update_storyline_node(self, node_id, updated_data):
        nodes = self.get_storyline_nodes()
        if node_id not in nodes:
            return None
        nodes[node_id].update(updated_data)
        self.set_storyline_nodes(nodes)
        return nodes[node_id]

    def delete_storyline_node(self, node_id):
        nodes = self.get_storyline_nodes()
        if node_id not in nodes:
            return False
        del nodes[node_id]
        self.set_storyline_nodes(nodes)
        return True

    def get_storyline_node(self, node_id):
        nodes = self.get_storyline_nodes()
        return nodes.get(node_id)
