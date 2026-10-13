import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import engine
import abilities
import item_types


ROOT = Path(__file__).parents[1]
ENGINE = ROOT / "engine.py"
EXAMPLE = ROOT / "example-turn.json"
MATERIAL_CULTURE = ROOT / "data" / "world_bible_material_culture.json"
ITEM_SYSTEM_GUIDE = ROOT / "data" / "world_bible_item_system_guide.json"
ABILITY_SYSTEM_GUIDE = ROOT / "data" / "world_bible_ability_system_guide.json"
MAGIC_CATALOG = ROOT / "data" / "world_bible_magic_catalog.json"
CORE_ENCYCLOPEDIA = ROOT / "data" / "world_bible_core_encyclopedia.json"
WORLD_BIBLE_MANIFEST = ROOT / "data" / "world_bible_manifest.json"
CHARACTER_PRESETS = ROOT / "data" / "character_presets.json"
IMPORT_WORLD_BIBLE = ROOT / "tools" / "import_world_bible.py"
CREATE_DELIVERY_PACKAGE = ROOT / "tools" / "create_delivery_package.py"


class EngineTests(unittest.TestCase):
    def command(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(ENGINE), *args], capture_output=True, text=True, check=check)

    def test_delivery_package_contains_every_server_runtime_import(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "secret-fire.zip"
            package_name = "Secret-Fire-Test"
            subprocess.run(
                [sys.executable, str(CREATE_DELIVERY_PACKAGE), "--output", str(output), "--name", package_name],
                capture_output=True, text=True, check=True,
            )
            server_source = (ROOT / "server.mjs").read_text(encoding="utf-8")
            relative_imports = set(re.findall(r'from "\./([^"?]+)"', server_source))
            with zipfile.ZipFile(output) as archive:
                packaged = set(archive.namelist())
            for imported in relative_imports:
                self.assertIn(f"{package_name}/{imported}", packaged)
            self.assertIn(f"{package_name}/dialogue-style.mjs", packaged)
            self.assertIn(f"{package_name}/http-boundary.mjs", packaged)
            self.assertFalse(any(name.endswith((".sqlite3", ".sqlite3-wal", ".sqlite3-shm")) for name in packaged))

    def test_ability_catalog_has_stable_cross_type_examples_and_hard_boundaries(self) -> None:
        catalog = abilities.ability_catalog()
        entries = catalog["abilities"]
        self.assertEqual(len(entries), 16)
        self.assertEqual(len({entry["id"] for entry in entries}), len(entries))
        self.assertEqual({entry["id"] for entry in catalog["forms"]}, {"specialty", "technique", "trait", "ritual"})
        self.assertTrue({"technique", "trait", "ritual"}.issubset({entry["form"] for entry in entries}))
        healing = abilities.ability_by_id("technique_stabilizing_touch")
        ritual = abilities.ability_by_id("ritual_waygate_passage")
        disarm = abilities.ability_by_id("technique_disarming_cut")
        self.assertIn("不等于完整治愈", healing["limits"])
        for requirement in ("完整仪式材料", "不受打扰的准备时间", "两端锚点已确认"):
            self.assertIn(requirement, ritual["requirements"])
        self.assertIn("二十点", disarm["limits"])

    def test_arno_preset_installs_and_restarts_as_one_complete_opening(self) -> None:
        catalog = json.loads(CHARACTER_PRESETS.read_text(encoding="utf-8"))
        self.assertEqual(catalog["version"], 1)
        self.assertEqual(len(catalog["presets"]), 1)
        preset = catalog["presets"][0]
        self.assertEqual(preset["id"], "arno")
        self.assertEqual(preset["title"], "Arno")
        self.assertNotIn("屠龙者的再集结", json.dumps(preset, ensure_ascii=False))
        self.assertRegex(preset["description"], r"死灵法师.{0,20}复活")
        self.assertIn("多支冒险者小队", preset["description"])
        self.assertIn("故事继续", preset["description"])
        self.assertEqual(
            {thread["id"] for thread in preset["setup"]["threads"]},
            {"shattered_valley_seal", "necromancer_revival_crisis", "royal_adventurer_recruitment"},
        )
        self.assertNotIn("明天下午，矿务使团", json.dumps(preset, ensure_ascii=False))

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            defaults = preset["defaults"]
            self.command(
                "--db", db, "init", "--campaign", "arno", "--title", "Arno",
                "--player", "Arno", "--concept", defaults["concept"],
                "--location", defaults["location"],
                "--character", json.dumps(defaults["character"], ensure_ascii=False),
                "--setup", json.dumps(preset["setup"], ensure_ascii=False),
            )

            def assert_opening() -> None:
                worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
                world = worlds["worlds"][0]
                self.assertEqual(world["title"], "Arno")
                self.assertEqual(world["player_name"], "Arno")
                self.assertEqual(world["player_state"]["mechanics"]["attributes"]["will"], 42)
                self.assertIn("久别重逢", world["current_scene"]["immediate_situation"])
                self.assertEqual(world["scene_model"]["pressures"], [])

                abilities_state = json.loads(self.command("--db", db, "abilities", "--campaign", "arno", "--json").stdout)
                self.assertEqual(
                    [entry["id"] for entry in abilities_state["abilities"]],
                    ["technique_oathbound_interception", "technique_stabilizing_touch"],
                )
                resources = json.loads(self.command("--db", db, "resources", "--campaign", "arno").stdout)
                self.assertEqual(resources["wallet"], {"currency": "copper", "balance": 1800})

                cast = json.loads(self.command("--db", db, "cast", "--campaign", "arno", "--json").stdout)
                self.assertEqual(len(cast["party"]), 4)
                orin = next(person for person in cast["party"] if person["id"] == "orin_veyth")
                self.assertEqual(orin["attributes"]["intellect"], 42)
                self.assertEqual(len(orin["abilities"]), 3)
                self.assertEqual(orin["ancestry"], "人类")
                self.assertEqual(orin["height_cm"], 179)
                self.assertEqual(orin["weight_kg"], 67)
                malka = next(person for person in cast["party"] if person["id"] == "malka_redanvil")
                self.assertIn("河港卫队副队长", malka["role"])
                self.assertNotIn("装卸工", malka["role"])

                possessions = json.loads(self.command("--db", db, "possessions", "--campaign", "arno", "--json").stdout)
                all_items = possessions["equipped"] + possessions["important"] + possessions["carried"] + possessions["elsewhere"]
                self.assertEqual(len(all_items), 24)
                self.assertEqual(len([item for item in all_items if item["holder"] == "player"]), 7)
                self.assertEqual(next(item for item in all_items if item["id"] == "evelyn_blood_rations")["quantity"], 2)

                brief = self.command("--db", db, "brief", "--campaign", "arno", "--action", "我在空椅上坐下，先和大家喝一杯。").stdout
                self.assertIn("王冠城 · 旧渡口 · 归锚酒馆", brief)
                self.assertIn("赛芮娅·月迹", brief)
                self.assertIn("technique_glimmer_lens", brief)
                self.assertIn("碎岩谷的异常", brief)
                self.assertIn("Active pressures: none recorded", brief)

            assert_opening()
            self.command("--db", db, "restart", "--campaign", "arno")
            assert_opening()

    def test_old_saves_have_no_abilities_and_only_relevant_owned_abilities_enter_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            empty = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual(empty["abilities"], [])
            self.assertEqual(empty["loads"], {"physical": "稳定", "focus": "稳定", "mystic": "稳定"})
            with sqlite3.connect(db) as connection:
                state = json.loads(connection.execute(
                    "SELECT state_json FROM entity_states WHERE entity_id='player'"
                ).fetchone()[0])
                state["mechanics"] = {
                    "abilities": [
                        {"id": "technique_flame_bolt", "mastery": "skilled"},
                        {"id": "trait_darkvision", "mastery": "novice"},
                        {"id": "technique_arcane_ward", "mastery": "mastered"},
                        {"id": "technique_disarming_cut", "mastery": "skilled"},
                    ],
                    "loads": {"mystic": "吃力"},
                }
                connection.execute(
                    "UPDATE entity_states SET state_json=? WHERE entity_id='player'",
                    (json.dumps(state, ensure_ascii=False),),
                )
            owned = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual([entry["name"] for entry in owned["abilities"]], ["火焰箭", "夜视", "奥术护盾", "缴械斩"])
            self.assertEqual(owned["loads"]["mystic"], "吃力")
            unrelated = self.command("--db", db, "brief", "--campaign", "test", "--action", "我喝一口水").stdout
            self.assertNotIn("Relevant owned abilities", unrelated)
            self.assertNotIn("technique_flame_bolt", unrelated)
            relevant = self.command("--db", db, "brief", "--campaign", "test", "--action", "我用火焰点燃吊桥绳索").stdout
            self.assertIn("Relevant owned abilities", relevant)
            self.assertIn("technique_flame_bolt", relevant)
            self.assertNotIn("trait_darkvision", relevant)

    def test_narrator_state_patch_cannot_grant_an_ability(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "turn.json"
            manifest.write_text(json.dumps({
                "player_action": "我回忆导师的教导。", "narration": "记忆依旧模糊。",
                "scene": {}, "entities": [],
                "state_updates": [{"entity_id": "player", "patch": {"mechanics": {
                    "abilities": [{"id": "technique_flame_bolt", "mastery": "mastered"}],
                    "loads": {"focus": "分散"},
                }}}],
                "events": [], "facts": [], "beliefs": [], "threads": [],
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            state = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual(state["abilities"], [])
            self.assertEqual(state["loads"]["focus"], "稳定")

    def test_validated_injuries_and_loads_follow_timeline_restoration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "turn.json"
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")

            def commit(consequences: list[dict], high_stakes: bool = False, narration: str = "玩家承受了后果。") -> subprocess.CompletedProcess[str]:
                manifest.write_text(json.dumps({
                    "player_action": "继续行动", "narration": narration,
                    "scene": {"resolution": {"high_stakes": high_stakes, "consequences": consequences}},
                    "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
                }, ensure_ascii=False), encoding="utf-8")
                return self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest), check=False)

            first = commit([
                {"type": "injury", "action": "add", "id": "sprained_ankle", "stage": "minor",
                 "label": "脚踝扭伤", "affected_functions": ["奔跑受限"], "source": "从石阶跌落",
                 "recovery_condition": "休息并固定脚踝", "permanent": False},
                {"type": "load", "track": "physical", "direction": "advance", "source": "长时间攀爬"},
            ])
            self.assertEqual(first.returncode, 0, first.stderr)
            state = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual(state["loads"]["physical"], "疲劳")
            self.assertEqual(state["injuries"][0]["stage"], "minor")
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "After fall")

            worsened = commit([{
                "type": "injury", "action": "worsen", "id": "sprained_ankle", "stage": "serious",
                "label": "脚踝韧带重伤", "affected_functions": ["无法正常负重"], "source": "带伤强行奔跑",
                "recovery_condition": "专业治疗和长期休养", "permanent": False,
            }])
            self.assertEqual(worsened.returncode, 0, worsened.stderr)
            state = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual(state["injuries"][0]["stage"], "serious")

            checkpoint = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)[0]
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "restored")
            restored = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual(restored["injuries"][0]["stage"], "minor")
            self.assertEqual(restored["loads"]["physical"], "疲劳")

            invalid = commit([{
                "type": "injury", "action": "add", "id": "sudden_critical", "stage": "critical",
                "label": "危重伤", "affected_functions": ["生命垂危"], "source": "普通失败",
                "recovery_condition": "紧急救治", "permanent": False,
            }])
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("critical injury requires explicit high stakes", invalid.stderr)

    def test_adjudication_context_exposes_only_recorded_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            empty = json.loads(self.command("--db", db, "adjudication-context", "--campaign", "test").stdout)
            self.assertNotIn("player", empty["attributes"])
            with sqlite3.connect(db) as connection:
                state = json.loads(connection.execute(
                    "SELECT state_json FROM entity_states WHERE branch_id='test:main' AND entity_id='player'"
                ).fetchone()[0])
                state["mechanics"] = {"attributes": {"physique": 24, "charisma": 31}}
                connection.execute(
                    "UPDATE entity_states SET state_json=? WHERE branch_id='test:main' AND entity_id='player'",
                    (json.dumps(state, ensure_ascii=False),),
                )
            recorded = json.loads(self.command("--db", db, "adjudication-context", "--campaign", "test").stdout)
            self.assertEqual(recorded["attributes"]["player"], {"physique": 24, "charisma": 31})

    def test_recorded_abilities_follow_checkpoint_restoration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "turn.json"
            manifest.write_text(json.dumps({
                "player_action": "我检查营地。", "narration": "营地仍然安静。", "scene": {},
                "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            with engine.connect(db) as connection:
                row = connection.execute(
                    "SELECT state_json FROM entity_states WHERE branch_id='test:main' AND entity_id='player'"
                ).fetchone()
                state = json.loads(row["state_json"])
                state["mechanics"] = {"abilities": [{"id": "trait_darkvision", "mastery": "skilled"}]}
                connection.execute(
                    "UPDATE entity_states SET state_json=? WHERE branch_id='test:main' AND entity_id='player'",
                    (json.dumps(state, ensure_ascii=False),),
                )
                engine.write_root(connection, "test:main", 0, engine.snapshot(connection, "test:main"))
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "with night sight")
            checkpoint = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)[0]
            with sqlite3.connect(db) as connection:
                current = json.loads(connection.execute(
                    "SELECT state_json FROM entity_states WHERE branch_id='test:main' AND entity_id='player'"
                ).fetchone()[0])
                current["mechanics"]["abilities"] = []
                connection.execute(
                    "UPDATE entity_states SET state_json=? WHERE branch_id='test:main' AND entity_id='player'",
                    (json.dumps(current, ensure_ascii=False),),
                )
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "ability_restore")
            restored = json.loads(self.command("--db", db, "abilities", "--campaign", "test", "--json").stdout)
            self.assertEqual([entry["id"] for entry in restored["abilities"]], ["trait_darkvision"])

    def test_relevant_ability_selection_is_capped_at_three(self) -> None:
        state = abilities.abilities_from_player_state({"mechanics": {
            "abilities": [entry["id"] for entry in abilities.ability_catalog()["abilities"]],
        }})
        selected = abilities.relevant_abilities(
            state,
            "我先用火焰箭，再展开奥术护盾，尝试缴械，同时靠夜视观察，并稳定伤势后开启传送门仪式。",
        )
        self.assertEqual(len(selected), 3)

    def test_item_system_guide_is_player_facing_and_importable(self) -> None:
        entries = json.loads(ITEM_SYSTEM_GUIDE.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 6)
        self.assertEqual({entry["category"] for entry in entries}, {"Items & equipment"})
        self.assertEqual(len({entry["title"] for entry in entries}), len(entries))
        self.assertTrue(all(entry["keys"] and entry["content"] for entry in entries))
        rarity_guide = next(entry for entry in entries if entry["title"] == "物品等级")["content"]
        for label in ("普通／常见", "稀有", "罕见", "传说", "神话"):
            self.assertIn(label, rarity_guide)
        self.assertIn("可追溯的专名、历史和重要经历", rarity_guide)
        self.assertIn("只记作未鉴定", rarity_guide)
        self.assertIn("普通街道", rarity_guide)
        self.assertIn("王室军械库", rarity_guide)
        self.assertIn("不会自动提高物品等级", rarity_guide)
        magic_items = next(entry for entry in entries if entry["title"] == "魔法物品与能力")["content"]
        for boundary in (
            "【施法媒介】", "本身不储存独立法术", "不会让持有者凭空获得能力",
            "【法器】", "使用法器不等于学会其中的术式",
            "【载体】", "【独立器具】", "【赋能物品】",
        ):
            self.assertIn(boundary, magic_items)
        trade_guide = next(entry for entry in entries if entry["title"] == "交易与钱包")["content"]
        for boundary in ("最小记账单位", "物品没有脱离情境的永久价格", "余额、物品归属与交易记录会同时更新", "不会在每一回合被自动估价"):
            self.assertIn(boundary, trade_guide)

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            for _ in range(2):
                subprocess.run([sys.executable, str(IMPORT_WORLD_BIBLE), "--db", db,
                                "--source", str(ITEM_SYSTEM_GUIDE)], capture_output=True, text=True, check=True)
            rows = json.loads(self.command("--db", db, "universe-lore", "--universe", "shattered_realms", "--json").stdout)
            self.assertEqual(len(rows), len(entries))
            self.assertTrue(all(row["category"] == "Items & equipment" for row in rows))

    def test_ability_system_guide_is_player_facing_and_importable(self) -> None:
        entries = json.loads(ABILITY_SYSTEM_GUIDE.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 6)
        self.assertEqual({entry["category"] for entry in entries}, {"Abilities & techniques"})
        self.assertEqual(len({entry["title"] for entry in entries}), len(entries))
        self.assertTrue(all(entry["keys"] and entry["secondaryKeys"] and entry["content"] for entry in entries))
        combined = "\n".join(entry["content"] for entry in entries)
        for concept in ("高灵能不等于会法术", "专业", "技法", "特性", "仪式", "初学", "熟练", "精通", "身体", "专注", "灵能"):
            self.assertIn(concept, combined)
        self.assertNotIn("state_json", combined)
        self.assertNotIn("AI", combined)

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            for _ in range(2):
                subprocess.run([sys.executable, str(IMPORT_WORLD_BIBLE), "--db", db,
                                "--source", str(ABILITY_SYSTEM_GUIDE)], capture_output=True, text=True, check=True)
            rows = json.loads(self.command("--db", db, "universe-lore", "--universe", "shattered_realms", "--json").stdout)
            self.assertEqual(len(rows), len(entries))
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我想举行传送仪式").stdout
            self.assertIn("维持、反制与大型仪式", brief)

    def test_magic_catalog_is_separate_searchable_and_covers_all_eight_circles(self) -> None:
        entries = json.loads(MAGIC_CATALOG.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 126)
        self.assertEqual({entry["category"] for entry in entries}, {"Magic & rituals", "Magic rules"})
        self.assertEqual(sum(entry["category"] == "Magic rules" for entry in entries), 10)
        self.assertEqual(sum(entry["category"] == "Magic & rituals" for entry in entries), 116)
        self.assertEqual(len({entry["title"] for entry in entries}), len(entries))
        self.assertTrue(all(entry["keys"] and entry["secondaryKeys"] and entry["content"] for entry in entries))
        circle_titles = {entry["title"] for entry in entries}
        for circle in "一二三四五六七八":
            self.assertIn(f"{circle}环法术：" + {
                "一": "微小改变与可靠手段", "二": "局部感知、护持与移动", "三": "场景应对与小队支援",
                "四": "场景塑形与持续守护", "五": "远距影响与重大抉择", "六": "领域控制与深度修复",
                "七": "跨域仪式与古老工程", "八": "边界、灾害与世界级责任",
            }[circle], circle_titles)
        self.assertIn("光亮术", circle_titles)
        self.assertIn("星界校正", circle_titles)
        self.assertEqual(sum(bool(entry.get("rename_by_order")) for entry in entries), 116)
        combined = "\n".join(entry["content"] for entry in entries)
        self.assertIn("不是角色等级、法术位、每日次数", combined)
        self.assertIn("不会随处提供高环术式", combined)

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            for _ in range(2):
                subprocess.run([sys.executable, str(IMPORT_WORLD_BIBLE), "--db", db,
                                "--source", str(MAGIC_CATALOG)], capture_output=True, text=True, check=True)
            rows = json.loads(self.command("--db", db, "universe-lore", "--universe", "shattered_realms", "--json").stdout)
            self.assertEqual(len(rows), len(entries))
            self.assertEqual(sum(row["category"] == "Magic rules" for row in rows), 10)
            self.assertEqual(sum(row["category"] == "Magic & rituals" for row in rows), 116)
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我想使用光亮术照亮阶梯").stdout
            self.assertIn("光亮术", brief)

    def test_world_bible_manifest_import_is_complete_and_idempotent(self) -> None:
        manifest = json.loads(WORLD_BIBLE_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], 1)
        self.assertEqual(manifest["universe"], "shattered_realms")
        source_paths = [ROOT / "data" / item["path"] for item in manifest["sources"]]
        self.assertTrue(all(path.is_file() for path in source_paths))
        expected = sum(len(json.loads(path.read_text(encoding="utf-8"))) for path in source_paths)
        source_ids = [entry["source_id"] for path in source_paths
                      for entry in json.loads(path.read_text(encoding="utf-8"))]
        self.assertEqual(len(source_ids), expected)
        self.assertEqual(len(set(source_ids)), expected)
        core_entries = json.loads(CORE_ENCYCLOPEDIA.read_text(encoding="utf-8"))
        lost_lands = next(entry for entry in core_entries if entry["title"] == "迷失之地")
        self.assertEqual(lost_lands["record"]["fields"]["current_campaign_region"], "环镜大陆的镜海西北部")
        self.assertEqual(lost_lands["record"]["fields"]["major_continents"], ["环镜大陆", "西雾大陆", "赤昼大陆"])
        self.assertIn("辉痕之地", lost_lands["content"])

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            command = [sys.executable, str(IMPORT_WORLD_BIBLE), "--db", db, "--all"]
            first = subprocess.run(command, capture_output=True, text=True, check=True)
            second = subprocess.run(command, capture_output=True, text=True, check=True)
            self.assertIn(f"{expected} created", first.stdout)
            self.assertIn("0 created", second.stdout)
            rows = json.loads(self.command("--db", db, "universe-lore", "--universe", "shattered_realms", "--json").stdout)
            self.assertEqual(len(rows), expected)
            self.assertEqual({row["source_id"] for row in rows}, set(source_ids))

    def test_world_bible_records_have_database_metadata_and_reach_brief(self) -> None:
        manifest = json.loads(WORLD_BIBLE_MANIFEST.read_text(encoding="utf-8"))
        sources = [ROOT / "data" / item["path"] for item in manifest["sources"]]
        records = [entry for path in sources for entry in json.loads(path.read_text(encoding="utf-8"))]
        structured = [entry for entry in records if isinstance(entry.get("record"), dict)]
        self.assertGreaterEqual(len(structured), 45)
        self.assertTrue(all(entry["record"].get("record_type") for entry in structured))
        self.assertTrue(all(entry["record"].get("canonical_name") for entry in structured))
        self.assertTrue(any(entry["record"].get("relations") for entry in structured))

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            subprocess.run([sys.executable, str(IMPORT_WORLD_BIBLE), "--db", db, "--all"], check=True, capture_output=True, text=True)
            rows = json.loads(self.command("--db", db, "universe-lore", "--universe", "shattered_realms", "--json").stdout)
            self.assertTrue(all(isinstance(row["record"], dict) for row in rows))
            self.assertTrue(all(row["record"].get("record_id") == row["source_id"] for row in rows))
            self.assertTrue(all(row["record"].get("source_category") == row["category"] for row in rows))
            self.assertTrue(all(isinstance(row["record"].get("retrieval"), dict) for row in rows))
            database_rule = next(row for row in rows if row["title"] == "数据库记录的真实性等级")
            self.assertEqual(database_rule["record"]["record_type"], "knowledge_rule")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我想了解王冠城的旅店和通行规则").stdout
            self.assertIn("record=", brief)
            self.assertIn("王冠城", brief)

    def test_item_names_are_instances_of_stable_categories(self) -> None:
        types = item_types.item_types()
        self.assertEqual(len(types), 370)
        self.assertEqual(len({entry["id"] for entry in types}), len(types))
        self.assertTrue(all(entry["signals"] and "reference" not in entry for entry in types))
        rarity_ids = {"common", "rare", "exceptional", "legendary", "mythic"}
        for entry in types:
            self.assertEqual(set(entry["rarity_guide"]), rarity_ids, entry["id"])
            self.assertTrue(all(profile["description"] for profile in entry["rarity_guide"].values()), entry["id"])
            expected_example_counts = {"common": 4, "rare": 3, "exceptional": 2, "legendary": 2, "mythic": 1}
            self.assertEqual(
                {rarity_id: len(profile["examples"]) for rarity_id, profile in entry["rarity_guide"].items()},
                expected_example_counts,
                entry["id"],
            )

        type_by_id = {entry["id"]: entry for entry in types}
        self.assertEqual(type_by_id["weapon.focus"]["category"], "Tools & everyday goods")
        self.assertEqual(sum(entry["category"] == "Weapons" for entry in types), 68)
        self.assertEqual(sum(entry["category"] == "Armor & protection" for entry in types), 47)
        self.assertEqual(sum(entry.get("group") == "Wearables & protection" for entry in types), 82)
        self.assertEqual(type_by_id["armor.heavy"]["group"], "Wearables & protection")
        self.assertEqual(type_by_id["clothing.top"]["group"], "Wearables & protection")
        self.assertEqual(type_by_id["clothing.top"]["label"], "衬衣")
        self.assertIn("clothing.tunic", type_by_id)
        self.assertEqual(type_by_id["tool.document"]["label"], "书籍")
        self.assertIn("food.stew", type_by_id)
        self.assertIn("medicine.injectable", type_by_id)
        self.assertIn("material.crystal", type_by_id)
        self.assertEqual(type_by_id["treasure.document"]["label"], "契约")
        self.assertIn("treasure.original_archive", type_by_id)
        self.assertIn("weapon.kukri", type_by_id)
        self.assertIn("armor.gorget", type_by_id)
        for entry in types:
            if entry["category"] in {"Weapons", "Armor & protection"}:
                self.assertFalse(any(mark in entry["label"] for mark in ("与", "、", "／")), entry["id"])
        self.assertEqual(type_by_id["tool.arcane_implement"]["category"], "Tools & everyday goods")
        sword_guide = type_by_id["weapon.sword"]["rarity_guide"]
        bread_guide = type_by_id["food.bread"]["rarity_guide"]
        self.assertNotEqual(sword_guide["rare"]["description"], bread_guide["rare"]["description"])
        self.assertIn("精制佩剑", sword_guide["rare"]["examples"])
        self.assertIn("王冠河谷面包", bread_guide["rare"]["examples"])
        siege_guide = type_by_id["weapon.siege"]["rarity_guide"]
        self.assertIn("制式弩炮", siege_guide["common"]["examples"])
        self.assertNotIn("重型武器", "；".join(siege_guide["common"]["examples"]))
        self.assertIn("「断潮者」：曾在北湾海战中改变战局", siege_guide["legendary"]["examples"])
        self.assertIn("「天裂」：据说一击便能撕开天幕", siege_guide["mythic"]["examples"])

        index = item_types.catalog_index()
        self.assertEqual(index["examples"], {})
        self.assertEqual(len(index["types"]), len(types))
        self.assertEqual(
            [rarity["id"] for rarity in index["rarities"]],
            ["common", "rare", "exceptional", "legendary", "mythic"],
        )
        self.assertTrue(all(rarity.get("instance_only") for rarity in index["rarities"][-2:]))
        ability_related_types = {
            "weapon.focus", "armor.ward", "tool.spell", "tool.magic", "tool.arcane_implement", "tool.ritual",
            "travel.flying", "travel.portal", "medicine.potion", "material.magic", "treasure.arcane",
        }
        self.assertTrue(all(item_types.baseline_for(type_id).get("ability_relation") for type_id in ability_related_types))
        self.assertNotIn("ability_relation", item_types.baseline_for("weapon.sword"))

        armor = item_types.classify_item({"name": "无敌皇家护甲", "description": "王冠城获得的一套重型铠甲，效果未知"})
        self.assertEqual((armor["base_type_id"], armor["reference_title"]), ("armor.heavy", None))
        self.assertIn("落水", item_types.baseline_for(armor["base_type_id"])["limits"])
        self.assertNotIn("无敌", json.dumps(armor, ensure_ascii=False))
        self.assertEqual(item_types.classify_item({"name": "魔法飞毯"})["base_type_id"], "travel.flying")
        self.assertIsNone(item_types.classify_item({"name": "看不出用途的奇物"})["base_type_id"])
        named_sword = item_types.classify_item({"name": "月蚀礼剑", "rarity": "exceptional"})
        self.assertEqual((named_sword["base_type_id"], named_sword["rarity"]), ("weapon.sword", "exceptional"))
        self.assertEqual(item_types.classify_item({"name": "破晓之刃", "base_type_id": "weapon.sword",
                                                   "rarity": "legendary"})["rarity"], "legendary")

        representative_items = {
            "兽人链锤": "weapon.flexible", "猎人标枪": "weapon.thrown",
            "学院法杖": "weapon.focus", "充能法器": "tool.arcane_implement", "城防弩炮": "weapon.siege",
            "炼金火油弹": "weapon.explosive", "捕兽夹": "weapon.trap",
            "矿工防尘面罩": "armor.hazard", "守护结界护符": "armor.ward",
            "战马马铠": "armor.mount", "码头工装": "clothing.workwear",
            "冬至祭服": "clothing.ceremonial", "航海日志": "tool.document",
            "留影镜": "tool.recording", "登山绳索": "tool.rigging",
            "肥皂": "tool.hygiene", "魔导装置": "tool.magic", "细剑": "weapon.rapier",
            "解毒剂": "medicine.antidote", "便携工坊": "tool.portable_workshop", "航图": "tool.map",
            "渡船": "travel.ferry", "古文书": "treasure.document",
            "木床": "tool.furniture", "沙漏": "tool.timekeeping",
            "遇险信标": "travel.rescue", "传送锚": "travel.portal",
            "新鲜苹果": "food.produce", "葡萄酒": "food.alcohol",
            "马料": "food.feed", "诊断器": "medicine.diagnostic",
            "消毒剂": "medicine.sanitation", "麻醉剂": "medicine.poison",
            "腐蚀剂": "medicine.alchemy", "陶土": "material.clay",
            "橡木板": "material.wood", "兽骨": "material.animal",
            "空白羊皮纸": "material.paper", "王室印玺": "treasure.ceremonial",
            "魔法遗物": "treasure.arcane_relic", "龙鳞标本": "treasure.natural",
        }
        for name, expected in representative_items.items():
            self.assertEqual(item_types.classify_item({"name": name})["base_type_id"], expected, name)

        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            item = {"id": "royal_armor", "name": "无敌皇家护甲", "description": "一套重型铠甲，效果未知",
                    "category": "important", "status": "equipped", "importance": 8}
            self.command("--db", db, "possession-upsert", "--campaign", "test", "--item", json.dumps(item, ensure_ascii=False))
            listed = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            armor_row = listed["equipped"][0]
            self.assertEqual((armor_row["name"], armor_row["base_type_id"], armor_row["reference_title"]),
                             ("无敌皇家护甲", "armor.heavy", None))
            self.assertEqual(armor_row["rarity"], "common")
            self.assertEqual(armor_row["rarity_label"], "普通／常见")
            self.assertIn("重甲", self.command("--db", db, "brief", "--campaign", "test", "--action", "检查铠甲").stdout)
            unknown = {"name": "看不出用途的奇物", "category": "important"}
            self.assertNotEqual(self.command("--db", db, "possession-upsert", "--campaign", "test",
                                             "--item", json.dumps(unknown, ensure_ascii=False), check=False).returncode, 0)
            unknown["base_type_id"] = "treasure.general"
            self.command("--db", db, "possession-upsert", "--campaign", "test", "--item", json.dumps(unknown, ensure_ascii=False))

            rare_sword = {"name": "同型试验剑", "base_type_id": "weapon.sword", "rarity": "rare"}
            exceptional_sword = {"name": "工坊校准剑", "base_type_id": "weapon.sword", "rarity": "exceptional"}
            legendary_sword = {"name": "破晓之刃", "base_type_id": "weapon.sword", "rarity": "legendary"}
            for entry in (rare_sword, exceptional_sword, legendary_sword):
                self.command("--db", db, "possession-upsert", "--campaign", "test",
                             "--item", json.dumps(entry, ensure_ascii=False))
            swords = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)["carried"]
            self.assertEqual({item["rarity"] for item in swords if item["base_type_id"] == "weapon.sword"},
                             {"rare", "exceptional", "legendary"})
            self.assertTrue(all("known_purpose" in item and not item["known_purpose"] for item in swords))

            unknown_relic = {"name": "无铭遗物", "base_type_id": "treasure.arcane", "rarity": "exceptional",
                             "rarity_known": False, "rarity_basis": "仅知来自封闭遗址，真实性尚未查明"}
            self.command("--db", db, "possession-upsert", "--campaign", "test",
                         "--item", json.dumps(unknown_relic, ensure_ascii=False))
            records = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            relic = next(item for group in ("equipped", "important", "carried", "elsewhere")
                         for item in records[group] if item["name"] == "无铭遗物")
            self.assertFalse(relic["rarity_known"])
            self.assertIn("封闭遗址", relic["rarity_basis"])

    def test_material_culture_connects_items_to_world_without_constant_context(self) -> None:
        entries = json.loads(MATERIAL_CULTURE.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 18)
        self.assertEqual(len({(entry["category"], entry["title"]) for entry in entries}), len(entries))
        self.assertTrue(all(entry["keys"] and entry["content"] for entry in entries))
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            for _ in range(2):
                subprocess.run([sys.executable, str(IMPORT_WORLD_BIBLE), "--db", db,
                                "--source", str(MATERIAL_CULTURE)], capture_output=True, text=True, check=True)
            rows = json.loads(self.command("--db", db, "universe-lore", "--universe", "shattered_realms", "--json").stdout)
            self.assertEqual(len(rows), len(entries))
            self.assertTrue(all(row["visibility"] == "public" and not row["constant"] for row in rows))
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "询问飞行器具的使用规矩").stdout
            self.assertIn("飞行器具与地面道路", brief)
            self.assertNotIn("寒港的冬备与归船", brief)

    def test_scene_state_persists_combat_until_the_story_changes_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = str(root / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "State", "--player", "Player")

            def commit(name: str, state, situation: str, model=None) -> dict:
                manifest = {
                    "player_action": name,
                    "narration": f"{name}确实发生了。",
                    "scene": {"location": "旧桥", "immediate_situation": situation},
                    "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
                }
                if state is not None:
                    manifest["scene"]["state"] = state
                if model is not None:
                    manifest["scene"]["model"] = model
                path = root / f"{name}.json"
                path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
                return json.loads(self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(path)).stdout)

            entered = commit("交战", {"activity": "exploration", "threat": "combat", "basis": "桥上的双方正在互相攻击"}, "桥上交战仍在继续。", {
                "player_position": "旧桥中央的石栏旁",
                "participants": [
                    {"id": "bridge_guard", "name": "桥卫", "position": "前方近处", "activity": "持矛逼近", "condition": "未受伤", "stance": "opposed"},
                ],
                "elements": [
                    {"id": "side_stairs", "name": "桥侧石阶", "kind": "route", "position": "玩家右后方", "state": "仍可通行"},
                ],
                "pressures": [
                    {"id": "closing_guard", "name": "逼近的桥卫", "text": "桥卫正在封住退路", "source": "桥卫", "urgency": "immediate"},
                ],
            })
            self.assertEqual(entered["scene_state"]["threat"], "combat")
            continued = commit("寻找掩体", None, "玩家躲到桥墩后，敌人仍在逼近。")
            self.assertEqual(continued["scene_state"]["threat"], "combat")
            self.assertEqual(continued["scene_model"]["elements"][0]["id"], "side_stairs")
            ended = commit("停战", {"activity": "dialogue", "threat": "aftermath", "basis": "双方已经放下武器"}, "双方已经停手。", {
                "player_position": "旧桥中央",
                "participants": [{"id": "bridge_guard", "name": "桥卫", "position": "数步外", "activity": "放下长矛", "condition": "气喘", "stance": "uncertain"}],
                "elements": [{"id": "side_stairs", "name": "桥侧石阶", "kind": "route", "position": "右后方", "state": "仍可通行"}],
                "pressures": [],
            })
            self.assertEqual(ended["scene_state"]["threat"], "aftermath")

            current = json.loads(self.command("--db", db, "scene-state", "--campaign", "test").stdout)
            self.assertEqual(current, {"activity": "dialogue", "threat": "aftermath", "basis": "双方已经放下武器"})
            worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual(worlds["worlds"][0]["scene_state"], current)
            self.assertEqual(worlds["worlds"][0]["scene_model"]["participants"][0]["activity"], "放下长矛")
            self.assertEqual(worlds["worlds"][0]["scene_model"]["pressures"], [])
            self.assertEqual(worlds["worlds"][0]["current_scene"]["immediate_situation"], "双方已经停手。")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "观察对方").stdout
            self.assertIn("Activity: dialogue; threat phase: aftermath", brief)
            self.assertIn("双方已经放下武器", brief)
            self.assertIn("桥侧石阶", brief)
            self.assertIn("放下长矛", brief)

    def test_gm_move_is_saved_for_cadence_and_defaults_to_none(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = str(root / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "World", "--player", "Player")
            manifest = {
                "player_action": "观察酒馆",
                "narration": "门一开，送酒人把新到的酒桶滚进吧台后方，腾出了通往后院的窄道。",
                "scene": {
                    "location": "旧酒馆",
                    "immediate_situation": "送酒人正在卸货，后院入口已经露出。",
                    "gm_move": {
                        "kind": "location_routine", "scope": "local", "source_id": "old_tavern",
                        "thread_id": "", "summary": "卸货腾出了通往后院的窄道", "basis": "酒馆正在接收每日酒水",
                    },
                },
                "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
            }
            path = root / "move.json"
            path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            committed = json.loads(self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(path)).stdout)
            self.assertEqual(committed["gm_move"]["kind"], "location_routine")
            self.assertEqual(committed["gm_move"]["scope"], "local")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "走近后门").stdout
            self.assertIn("Previous GM move: location_routine (local)", brief)
            self.assertIn("卸货腾出了通往后院的窄道", brief)

            manifest["player_action"] = "整理袖口"
            manifest["narration"] = "他整理好袖口，酒馆里的谈笑仍照常继续。"
            manifest["scene"].pop("gm_move")
            path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            quiet = json.loads(self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(path)).stdout)
            self.assertEqual(quiet["gm_move"]["kind"], "none")

            manifest["player_action"] = "继续听酒馆里的声音"
            manifest["narration"] = "酒馆里的杯碟声没有带来新的变化。"
            manifest["scene"]["gm_move"] = {"kind": "discovery", "scope": "local", "summary": ""}
            path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            incomplete = json.loads(self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(path)).stdout)
            self.assertEqual(incomplete["gm_move"]["kind"], "none")

    def test_world_removal_is_recoverable_and_does_not_touch_other_worlds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "first", "--title", "Same title", "--player", "One")
            self.command("--db", db, "commit", "--campaign", "first", "--manifest", str(EXAMPLE))
            self.command("--db", db, "init", "--campaign", "second", "--title", "Same title", "--player", "Two")
            self.command("--db", db, "trash-world", "--campaign", "second")
            state = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual([world["id"] for world in state["worlds"]], ["first"])
            self.assertEqual([world["id"] for world in state["trashed_worlds"]], ["second"])
            self.assertEqual(state["active_campaign"], "first")
            self.assertNotEqual(self.command("--db", db, "select-world", "--campaign", "second", check=False).returncode, 0)
            self.command("--db", db, "restore-world", "--campaign", "second")
            state = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual({world["id"] for world in state["worlds"]}, {"first", "second"})
            self.assertEqual(json.loads(self.command("--db", db, "timeline", "--campaign", "first", "--json").stdout)[0]["turn_number"], 1)

    def test_permanent_delete_only_purges_a_trashed_world(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "keep", "--title", "Same title", "--player", "Keep")
            self.command("--db", db, "commit", "--campaign", "keep", "--manifest", str(EXAMPLE))
            with sqlite3.connect(db) as conn:
                universe = conn.execute("SELECT universe_id FROM campaign_universes WHERE campaign_id='keep'").fetchone()[0]
                conn.execute("INSERT INTO universe_lore_entries(id, universe_id, title, content, created_at) VALUES (?, ?, ?, ?, ?)",
                             ("shared_lore", universe, "Shared", "Belongs to the universe", "2026-01-01"))
            self.command("--db", db, "init", "--campaign", "discard", "--title", "Same title", "--player", "Discard")
            self.command("--db", db, "commit", "--campaign", "discard", "--manifest", str(EXAMPLE))
            self.command("--db", db, "checkpoint", "--campaign", "discard", "--name", "Before fork")
            with sqlite3.connect(db) as conn:
                checkpoint = conn.execute("SELECT id FROM checkpoints WHERE campaign_id='discard'").fetchone()[0]
            self.command("--db", db, "restore", "--campaign", "discard", "--checkpoint", checkpoint, "--name", "other_path")
            self.assertNotEqual(self.command("--db", db, "purge-world", "--campaign", "discard", check=False).returncode, 0)
            self.command("--db", db, "trash-world", "--campaign", "discard")
            self.command("--db", db, "purge-world", "--campaign", "discard")
            state = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual([item["id"] for item in state["worlds"]], ["keep"])
            self.assertEqual(state["trashed_worlds"], [])
            self.assertEqual(len(json.loads(self.command("--db", db, "timeline", "--campaign", "keep", "--json").stdout)), 1)
            self.assertNotEqual(self.command("--db", db, "restore-world", "--campaign", "discard", check=False).returncode, 0)
            with sqlite3.connect(db) as conn:
                self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(conn.execute("SELECT count(*) FROM branches WHERE campaign_id='discard'").fetchone()[0], 0)
                self.assertEqual(conn.execute("SELECT count(*) FROM campaigns WHERE id='discard'").fetchone()[0], 0)
                self.assertGreater(conn.execute("SELECT count(*) FROM universe_lore_entries").fetchone()[0], 0)

    def test_map_tracks_reached_places_per_timeline_and_guides_scene_tone(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Map", "--player", "Player", "--location", "精灵酒馆")
            opening = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            self.assertEqual(opening["current"], "精灵酒馆")
            self.assertEqual(opening["current_profile"]["mood"], "放松而热闹")
            self.assertEqual(engine.location_profile("王冠城·旧渡口")["source"], "established_start")
            self.assertEqual(opening["routes"], [])
            self.assertIn("放松而热闹", self.command("--db", db, "brief", "--campaign", "test", "--action", "点一杯茶").stdout)
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "Before valley")
            checkpoint = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)[0]
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "valley_path")
            manifest = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            manifest["scene"]["location"] = "黑龙山谷"
            manifest["state_updates"] = [{"entity_id": "player", "patch": {"location": "黑龙山谷"}}]
            manifest_path = Path(directory) / "valley.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest_path))
            branch_map = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            self.assertEqual(branch_map["current"], "黑龙山谷")
            self.assertEqual(branch_map["current_profile"]["source"], "name_hint")
            self.assertEqual(len(branch_map["routes"]), 2)
            self.command("--db", db, "checkout", "--campaign", "test", "--branch", "main")
            main_map = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            self.assertNotIn("黑龙山谷", [place["name"] for place in main_map["places"]])

    def test_concrete_places_survive_departure_and_return_as_the_same_instance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command(
                "--db", db, "init", "--campaign", "test", "--title", "Places",
                "--player", "Player", "--location", "晨星酒馆",
            )
            opening = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            tavern_id = opening["current_id"]
            self.assertTrue(tavern_id.startswith("location_"))
            self.assertEqual(opening["places"][0]["visits"], 1)

            def commit(filename: str, action: str, location: str, record: dict) -> None:
                path = Path(directory) / filename
                path.write_text(json.dumps({
                    "player_action": action,
                    "narration": f"Player arrives at {location}.",
                    "scene": {"location": location, "location_record": record},
                    "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
                }, ensure_ascii=False), encoding="utf-8")
                self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(path))

            commit("tavern.json", "环顾酒馆", "晨星酒馆", {
                "id": "morningstar_tavern", "name": "晨星酒馆", "kind": "building",
                "parent_id": "crown_city_riverside", "parent_name": "王冠城河岸区",
                "description": "一间由旧仓库改成的临河酒馆。", "atmosphere": "温暖而嘈杂",
                "current_summary": "店主仍是阿妲，二楼东间留给熟客。", "features": ["临河后门", "二楼东间"],
            })
            after_detail = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            self.assertEqual(after_detail["current_id"], tavern_id)
            self.assertEqual(after_detail["current_place"]["parent_name"], "王冠城河岸区")
            self.assertEqual(after_detail["current_place"]["visits"], 1)

            commit("street.json", "走到街上", "风铃街", {
                "id": "wind_chime_street", "name": "风铃街", "kind": "street",
                "parent_id": "crown_city_riverside", "parent_name": "王冠城河岸区",
                "description": "沿河铺开的石街。",
            })
            away = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            self.assertEqual(away["current"], "风铃街")
            saved_tavern = next(place for place in away["places"] if place["id"] == tavern_id)
            self.assertEqual(saved_tavern["current_summary"], "店主仍是阿妲，二楼东间留给熟客。")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我返回晨星酒馆").stdout
            self.assertIn(f"晨星酒馆 (`{tavern_id}`", brief)
            self.assertIn("店主仍是阿妲", brief)

            commit("return.json", "返回酒馆", "晨星酒馆", {"id": tavern_id, "name": "晨星酒馆"})
            returned = json.loads(self.command("--db", db, "map", "--campaign", "test", "--json").stdout)
            self.assertEqual(returned["current_id"], tavern_id)
            self.assertEqual(returned["current_place"]["visits"], 2)
            self.assertEqual(returned["current_place"]["description"], "一间由旧仓库改成的临河酒馆。")
            self.assertEqual(returned["routes"][0]["uses"], 2)

            connection = sqlite3.connect(db)
            connection.row_factory = sqlite3.Row
            player = connection.execute(
                "SELECT state_json FROM entity_states WHERE branch_id='test:main' AND entity_id='player'"
            ).fetchone()
            self.assertEqual(json.loads(player["state_json"])["location_id"], tavern_id)
            connection.close()

    def test_commit_builds_brief_and_branch_preserves_main(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            character = json.dumps({"ancestry": "Elf", "origin": "Salt Road", "bond": "The ferry family"}, ensure_ascii=False)
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player", "--character", character)
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
            recent = json.loads(self.command("--db", db, "recent-prose", "--campaign", "test").stdout)
            self.assertEqual(len(recent), 1)
            self.assertIn("黑鸦酒馆", recent[0]["narration"])
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "问伊莲娜戒指的事").stdout
            self.assertIn("王室纹章戒指", brief)
            self.assertIn("伊莲娜", brief)
            self.assertIn("Salt Road", brief)
            self.command("--db", db, "branch", "--campaign", "test", "--from-turn", "1", "--name", "refusal")
            branched_brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "拒绝戒指").stdout
            self.assertIn("王室纹章戒指", branched_brief)
            self.assertIn("黑鸦酒馆后巷", branched_brief)
            state = self.command("--db", db, "status", "--campaign", "test").stdout
            self.assertIn("main", state)
            self.assertIn("refusal", state)

    def test_manifest_requires_story_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "bad.json"
            manifest.write_text(json.dumps({"player_action": "look"}), encoding="utf-8")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            result = self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest), check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("narration", result.stderr)

    def test_key_possessions_are_prompted_and_follow_a_rollback_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "possessions.json"
            manifest.write_text(json.dumps({
                "player_action": "我把月银钥匙藏进外套，戴上母亲的护符。",
                "narration": "钥匙贴在胸前，护符在衣领下微微发热。",
                "scene": {"location": "Old Road"},
                "entities": [
                    {"id": "item_moonsilver_key", "type": "item", "name": "月银钥匙",
                     "profile": {"category": "clue", "description": "一把带冷光的细钥匙", "known_purpose": "可开启月门", "tags": ["月门"]},
                     "state": {"holder": "player", "status": "concealed", "importance": 9, "quantity": 1}},
                    {"id": "item_mothers_amulet", "type": "item", "name": "母亲的护符",
                     "profile": {"category": "gear", "description": "银质护符"},
                     "state": {"holder": "player", "status": "equipped", "equipped_as": "under collar", "importance": 6, "quantity": 1}},
                    {"id": "item_breakfast", "type": "item", "name": "干粮",
                     "profile": {"category": "ordinary"},
                     "state": {"holder": "player", "status": "carried", "importance": 1, "quantity": 2}}
                ], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            possessions = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual([item["name"] for item in possessions["equipped"]], ["母亲的护符"])
            self.assertEqual([item["name"] for item in possessions["important"]], ["月银钥匙"])
            self.assertEqual([item["name"] for item in possessions["carried"]], ["干粮"])
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我看向远处的街道").stdout
            self.assertIn("月银钥匙", brief)
            self.assertIn("母亲的护符", brief)
            self.assertNotIn("干粮", brief)
            manifest.write_text(json.dumps({
                "player_action": "我把钥匙交给守门人。", "narration": "守门人没有接，只让钥匙继续藏在你身上。",
                "scene": {"location": "Moon Gate"},
                "entities": [{"id": "item_moonsilver_key", "type": "item", "name": "月银钥匙",
                              "state": {"status": "concealed", "importance": 9}}],
                "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            updated = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual(updated["important"][0]["known_purpose"], "可开启月门")
            manifest.write_text(json.dumps({
                "player_action": "我问守门人钥匙在哪里。", "narration": "守门人摇了摇头。",
                "scene": {"location": "Moon Gate"}, "entities": [],
                "state_updates": [{"entity_id": "item_moonsilver_key", "patch": {"holder": "guardian", "status": "given"}}],
                "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            guarded = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual(guarded["important"][0]["holder"], "player")
            self.command("--db", db, "branch", "--campaign", "test", "--from-turn", "2", "--name", "return_to_road")
            branched = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual([item["name"] for item in branched["important"]], ["月银钥匙"])

    def test_trade_cycle_is_atomic_and_updates_wallet_items_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "trade.json"
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")

            def story_turn(offer: dict, narration: str) -> None:
                manifest.write_text(json.dumps({
                    "player_action": "处理眼前的交易。", "narration": narration,
                    "scene": {"location": "集市", "state": {"activity": "trade"}, "_trade_offers": [offer]},
                    "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
                }, ensure_ascii=False), encoding="utf-8")
                self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))

            reward_id = "trade_11111111111111111111111111111111"
            story_turn({
                "id": reward_id, "kind": "reward", "counterparty": "商队管事",
                "quantity": 1, "unit_price": 250, "reason": "护送报酬",
            }, "商队管事把二百五十枚铜币的报酬放在桌上，等你收下。")
            initial = json.loads(self.command("--db", db, "resources", "--campaign", "test").stdout)
            self.assertEqual(initial["wallet"]["balance"], 0)
            self.assertEqual([offer["id"] for offer in initial["pending_offers"]], [reward_id])
            reward = json.loads(self.command(
                "--db", db, "trade-commit", "--campaign", "test", "--offer", reward_id
            ).stdout)
            self.assertEqual(reward["resources"]["wallet"]["balance"], 250)
            self.assertEqual(reward["transaction"]["amount"], 250)
            self.assertEqual(reward["resources"]["pending_offers"], [])

            buy_id = "trade_22222222222222222222222222222222"
            story_turn({
                "id": buy_id, "kind": "buy", "counterparty": "铁匠哈伦",
                "quantity": 2, "unit_price": 60, "reason": "两把普通铁剑",
                "item": {"name": "铁剑", "category": "gear", "base_type_id": "weapon.sword",
                         "rarity": "common", "description": "普通铁制单手剑", "importance": 3},
            }, "铁匠哈伦报出每把六十枚铜币的价格，等你决定是否买下两把铁剑。")
            purchase = json.loads(self.command(
                "--db", db, "trade-commit", "--campaign", "test", "--offer", buy_id
            ).stdout)
            self.assertEqual(purchase["resources"]["wallet"]["balance"], 130)
            bought = purchase["possessions"]["carried"][0]
            self.assertEqual((bought["name"], bought["quantity"], bought["base_type_id"]),
                             ("铁剑", 2, "weapon.sword"))

            sell_id = "trade_33333333333333333333333333333333"
            story_turn({
                "id": sell_id, "kind": "sell", "counterparty": "旧货商",
                "item_id": bought["id"], "quantity": 1, "unit_price": 45, "reason": "回收一把铁剑",
            }, "旧货商愿意用四十五枚铜币收下一把铁剑。")
            sale = json.loads(self.command(
                "--db", db, "trade-commit", "--campaign", "test", "--offer", sell_id
            ).stdout)
            self.assertEqual(sale["resources"]["wallet"]["balance"], 175)
            self.assertEqual(sale["possessions"]["carried"][0]["quantity"], 1)
            self.assertEqual([entry["kind"] for entry in sale["resources"]["transactions"]],
                             ["reward", "buy", "sell"])
            trade_brief = self.command(
                "--db", db, "brief", "--campaign", "test", "--action", "我想把铁剑卖给旧货商"
            ).stdout
            self.assertIn(bought["id"], trade_brief)
            self.assertIn("quantity=1", trade_brief)

            replay = self.command(
                "--db", db, "trade-commit", "--campaign", "test", "--offer", sell_id, check=False
            )
            self.assertNotEqual(replay.returncode, 0)
            after_replay = json.loads(self.command("--db", db, "resources", "--campaign", "test").stdout)
            self.assertEqual(after_replay["wallet"]["balance"], 175)
            self.assertEqual(len(after_replay["transactions"]), 3)

    def test_failed_trade_has_no_partial_effect_and_resources_follow_checkpoint_restore(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "trade.json"
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")

            def commit_offer(offer: dict, narration: str = "对方提出了明确报价。") -> None:
                manifest.write_text(json.dumps({
                    "player_action": "继续", "narration": narration,
                    "scene": {"location": "码头", "_trade_offers": [offer]},
                    "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": [],
                }, ensure_ascii=False), encoding="utf-8")
                self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))

            reward_id = "trade_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            commit_offer({"id": reward_id, "kind": "reward", "counterparty": "船长", "quantity": 1,
                          "unit_price": 80, "reason": "搬运报酬"})
            self.command("--db", db, "trade-commit", "--campaign", "test", "--offer", reward_id)
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "with wages")
            checkpoint = json.loads(self.command(
                "--db", db, "checkpoints", "--campaign", "test", "--json"
            ).stdout)[0]

            expensive_id = "trade_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            commit_offer({
                "id": expensive_id, "kind": "buy", "counterparty": "船具商", "quantity": 1,
                "unit_price": 500, "reason": "一张航海图",
                "item": {"name": "航海图", "category": "important", "base_type_id": "travel.navigation",
                         "rarity": "common", "description": "标有近岸航道的图纸"},
            })
            turns_before = sqlite3.connect(db).execute("SELECT COUNT(*) FROM turns").fetchone()[0]
            failed = self.command(
                "--db", db, "trade-commit", "--campaign", "test", "--offer", expensive_id, check=False
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("insufficient funds", failed.stderr)
            with sqlite3.connect(db) as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM turns").fetchone()[0], turns_before)
            unchanged = json.loads(self.command("--db", db, "resources", "--campaign", "test").stdout)
            self.assertEqual(unchanged["wallet"]["balance"], 80)
            self.assertEqual(len(unchanged["transactions"]), 1)
            self.assertEqual(json.loads(self.command(
                "--db", db, "possessions", "--campaign", "test", "--json"
            ).stdout)["carried"], [])

            payment_id = "trade_cccccccccccccccccccccccccccccccc"
            commit_offer({"id": payment_id, "kind": "payment", "counterparty": "港务员", "quantity": 1,
                          "unit_price": 30, "reason": "靠泊费"})
            self.command("--db", db, "trade-commit", "--campaign", "test", "--offer", payment_id)
            self.assertEqual(json.loads(self.command(
                "--db", db, "resources", "--campaign", "test"
            ).stdout)["wallet"]["balance"], 50)

            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "before_fee")
            restored = json.loads(self.command("--db", db, "resources", "--campaign", "test").stdout)
            self.assertEqual(restored["wallet"]["balance"], 80)
            self.assertEqual([entry["kind"] for entry in restored["transactions"]], ["reward"])

    def test_narrator_state_patch_cannot_change_wallet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "turn.json"
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            manifest.write_text(json.dumps({
                "player_action": "我希望自己突然富有。", "narration": "愿望没有改变钱袋。", "scene": {},
                "entities": [], "state_updates": [{"entity_id": "player", "patch": {"mechanics": {
                    "resources": {"wallet": {"currency": "copper", "balance": 999999}}
                }}}], "events": [], "facts": [], "beliefs": [], "threads": [],
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            resources = json.loads(self.command("--db", db, "resources", "--campaign", "test").stdout)
            self.assertEqual(resources["wallet"]["balance"], 0)
            self.assertEqual(resources["transactions"], [])

    def test_local_possession_revision_is_hidden_from_story_and_restores_with_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            item = json.dumps({"name": "旅人的地图", "category": "clue", "status": "carried", "importance": 8,
                               "description": "标出旧盐路的羊皮地图", "known_purpose": "寻找渡口"}, ensure_ascii=False)
            self.command("--db", db, "possession-upsert", "--campaign", "test", "--item", item)
            listed = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual(listed["important"][0]["name"], "旅人的地图")
            self.assertEqual(listed["important"][0]["base_type_id"], "travel.navigation")
            timeline = json.loads(self.command("--db", db, "timeline", "--campaign", "test", "--json").stdout)
            self.assertEqual(timeline, [])
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "map saved")
            checkpoint = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)[0]
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "map_branch")
            restored = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual(restored["important"][0]["known_purpose"], "寻找渡口")
            self.assertEqual(restored["important"][0]["base_type_id"], "travel.navigation")

    def test_item_card_tracks_holder_without_treating_gift_as_player_gear(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            person = json.dumps({"id": "mara", "name": "玛拉", "status": "party", "objective": "寻找渡口"}, ensure_ascii=False)
            self.command("--db", db, "cast-upsert", "--campaign", "test", "--person", person)
            item = json.dumps({"id": "silver_key", "name": "银钥匙", "category": "clue", "status": "given",
                               "holder": "mara", "location": "旧渡口", "importance": 8}, ensure_ascii=False)
            self.command("--db", db, "possession-upsert", "--campaign", "test", "--item", item)
            listed = json.loads(self.command("--db", db, "possessions", "--campaign", "test", "--json").stdout)
            self.assertEqual(listed["important"], [])
            self.assertEqual([(row["name"], row["holder"], row["location"]) for row in listed["elsewhere"]],
                             [("银钥匙", "mara", "旧渡口")])
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我问玛拉银钥匙在哪里").stdout
            self.assertIn("holder=mara", brief)
            self.assertIn("status=given", brief)
            bad = json.dumps({"name": "假钥匙", "status": "given", "holder": "missing_npc"}, ensure_ascii=False)
            self.assertNotEqual(self.command("--db", db, "possession-upsert", "--campaign", "test", "--item", bad, check=False).returncode, 0)

    def test_party_people_persist_in_context_and_restore_with_a_timeline(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "people.json"
            manifest.write_text(json.dumps({
                "player_action": "我邀请玛拉同行。", "narration": "玛拉把弓背到肩上，答应陪你走到河口。",
                "scene": {"location": "Old Road", "present_entities": ["mara_sunvale"]},
                "entities": [{"id": "mara_sunvale", "type": "npc", "name": "玛拉·晴谷",
                              "profile": {"role": "林径向导", "description": "总带着一把榆木弓", "aliases": ["玛拉"]},
                              "state": {"status": "party", "tier": "core", "relationship": "刚结伴的向导", "location": "Old Road",
                                        "anchor": "答应护送你抵达河口", "memory_event": {"text": "她在旧路上答应同行。", "kind": "promise", "importance": 8}}}],
                "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            cast = json.loads(self.command("--db", db, "cast", "--campaign", "test", "--json").stdout)
            self.assertEqual(cast["party"][0]["name"], "玛拉·晴谷")
            self.assertEqual(cast["party"][0]["memories"][0]["text"], "她在旧路上答应同行。")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我检查河边的足迹").stdout
            self.assertIn("玛拉·晴谷", brief)
            self.assertIn("答应护送你抵达河口", brief)
            manifest.write_text(json.dumps({
                "player_action": "我替玛拉挡下落石。", "narration": "玛拉拉住你的手臂，低声说自己欠你一次。",
                "scene": {"location": "River Cliffs", "present_entities": ["mara_sunvale"]}, "entities": [],
                "state_updates": [{"entity_id": "mara_sunvale", "patch": {"location": "River Cliffs", "relationship": "同行的向导，也欠你一次救命之情", "memory_event": {"text": "你替她挡下了落石。", "kind": "rescue", "importance": 9}}}],
                "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            updated = json.loads(self.command("--db", db, "cast", "--campaign", "test", "--json").stdout)
            self.assertEqual(len(updated["party"][0]["memories"]), 2)
            self.assertIn("救命", updated["party"][0]["relationship"])
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "with mara")
            checkpoint = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)[0]
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "mara_branch")
            restored = json.loads(self.command("--db", db, "cast", "--campaign", "test", "--json").stdout)
            self.assertEqual(restored["party"][0]["relationship"], "同行的向导，也欠你一次救命之情")

    def test_people_memory_limits_follow_story_role(self) -> None:
        memories = [
            {"text": f"重要经历 {index}", "importance": index % 10 + 1, "turn": index, "kind": "event"}
            for index in range(40)
        ]
        party = engine.normalize_npc_state({}, {"status": "party", "tier": "core", "memories": memories}, 40)
        recurring = engine.normalize_npc_state({}, {"status": "known", "tier": "recurring", "memories": memories}, 40)
        background = engine.normalize_npc_state({}, {"status": "known", "tier": "background", "memories": memories}, 40)
        self.assertEqual(len(party["memories"]), 30)
        self.assertEqual(len(recurring["memories"]), 18)
        self.assertEqual(len(background["memories"]), 12)

    def test_partial_npc_entity_update_preserves_name_type_and_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "people.json"
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            manifest.write_text(json.dumps({
                "player_action": "我向玛拉问路。", "narration": "玛拉报上姓名，答应带路。",
                "scene": {"location": "Old Road", "present_entities": ["mara"]},
                "entities": [{"id": "mara", "type": "npc", "name": "玛拉",
                              "profile": {"role": "林径向导", "voice": "说话简短"},
                              "state": {"status": "party", "tier": "core", "objective": "找到渡口"}}],
                "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            manifest.write_text(json.dumps({
                "player_action": "我问她下一步。", "narration": "玛拉展开地图，开始核对河道。",
                "scene": {"location": "Old Road", "present_entities": ["mara"]},
                "entities": [{"id": "mara", "state": {"activity": "展开地图核对河道", "next_move": "沿河岸找旧路标"}}],
                "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(manifest))
            cast = json.loads(self.command("--db", db, "cast", "--campaign", "test", "--json").stdout)
            mara = cast["party"][0]
            self.assertEqual(mara["name"], "玛拉")
            self.assertEqual(mara["role"], "林径向导")
            self.assertEqual(mara["voice"], "说话简短")
            self.assertEqual(mara["activity"], "展开地图核对河道")
            with engine.connect(db) as connection:
                entity = connection.execute(
                    "SELECT type FROM entities WHERE campaign_id='test' AND id='mara'"
                ).fetchone()
            self.assertEqual(entity["type"], "npc")

    def test_named_checkpoint_restores_as_timeline_and_restart_reclaims_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            character = json.dumps({"ancestry": "Dwarf", "burden": "A broken oath"}, ensure_ascii=False)
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player", "--location", "Inn", "--character", character)
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "第一幕入口")
            saves = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)
            self.assertEqual(saves[0]["name"], "第一幕入口")
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", saves[0]["id"], "--name", "alternate")
            restored = self.command("--db", db, "brief", "--campaign", "test", "--action", "继续前行").stdout
            self.assertIn("王室纹章戒指", restored)
            self.command("--db", db, "checkout", "--campaign", "test", "--branch", "main")
            self.command("--db", db, "delete-branch", "--campaign", "test", "--branch", "alternate")
            self.command("--db", db, "restart", "--campaign", "test")
            restarted = self.command("--db", db, "brief", "--campaign", "test", "--action", "开始").stdout
            self.assertIn("broken oath", restarted)
            self.assertIn("Inn", restarted)
            self.assertIn("Campaign has not started", restarted)

    def test_timeline_includes_history_before_a_restored_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
            self.command("--db", db, "checkpoint", "--campaign", "test", "--name", "Before the choice")
            checkpoint = json.loads(self.command("--db", db, "checkpoints", "--campaign", "test", "--json").stdout)[0]
            self.command("--db", db, "restore", "--campaign", "test", "--checkpoint", checkpoint["id"], "--name", "alternate")
            restored_timeline = json.loads(self.command("--db", db, "timeline", "--campaign", "test", "--json").stdout)
            self.assertEqual([turn["turn_number"] for turn in restored_timeline], [1])
            self.assertIn("王室纹章戒指", restored_timeline[0]["player_action"])
            worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual(worlds["worlds"][0]["turn_count"], 1)

    def test_worldbook_is_budgeted_and_triggered_by_current_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            self.command(
                "--db", db, "lore-add", "--campaign", "test", "--title", "The Moon Gate",
                "--content", "The Moon Gate opens only when a silver key is placed in its lock.",
                "--keys", "moon gate,silver key", "--priority", "70",
            )
            self.command(
                "--db", db, "lore-add", "--campaign", "test", "--title", "Narrative rule",
                "--content", "Magic is visible only to those who have sworn an oath.", "--constant",
            )
            active = self.command("--db", db, "brief", "--campaign", "test", "--action", "I examine the silver key beside the Moon Gate").stdout
            inactive = self.command("--db", db, "brief", "--campaign", "test", "--action", "I order breakfast at the inn").stdout
            self.assertIn("The Moon Gate opens", active)
            self.assertNotIn("The Moon Gate opens", inactive)
            self.assertIn("Magic is visible", active)
            self.assertIn("Magic is visible", inactive)

    def test_compact_journal_keeps_arbitrary_branching_recoverable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            for _ in range(26):
                self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
            with sqlite3.connect(db) as connection:
                snapshots = connection.execute("SELECT COUNT(*) FROM snapshots WHERE branch_id='test:main'").fetchone()[0]
                roots = connection.execute("SELECT COUNT(*) FROM state_roots WHERE branch_id='test:main'").fetchone()[0]
                deltas = connection.execute("SELECT COUNT(*) FROM state_deltas WHERE branch_id='test:main'").fetchone()[0]
            # A separate turn-zero root plus the periodic anchor at turn 25.
            # The 26 playable turns are row-level journals, not 26 full copies.
            self.assertEqual(roots, 1)
            self.assertEqual(snapshots, 1)
            self.assertEqual(deltas, 26)
            self.command("--db", db, "branch", "--campaign", "test", "--from-turn", "13", "--name", "midpoint")
            restored = self.command("--db", db, "brief", "--campaign", "test", "--action", "继续前进").stdout
            self.assertIn("王室纹章戒指", restored)

    def test_compact_converts_legacy_snapshots_without_losing_branch_points(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            # Build a small representation of the original all-full-snapshot
            # format, then prove the migration can branch from its middle.
            for turn_number in range(1, 4):
                self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
                with engine.connect(db) as connection, connection:
                    data = engine.snapshot(connection, "test:main")
                    connection.execute(
                        "INSERT INTO snapshots(branch_id, turn_id, turn_number, snapshot_json) VALUES (?, ?, ?, ?)",
                        ("test:main", f"test:main:turn:{turn_number}", turn_number, json.dumps(data, ensure_ascii=False)),
                    )
            with sqlite3.connect(db) as connection, connection:
                connection.execute("DELETE FROM state_roots")
                connection.execute("DELETE FROM state_deltas")
            self.command("--db", db, "compact", "--campaign", "test")
            with sqlite3.connect(db) as connection:
                snapshots = connection.execute("SELECT COUNT(*) FROM snapshots WHERE branch_id='test:main'").fetchone()[0]
                deltas = connection.execute("SELECT COUNT(*) FROM state_deltas WHERE branch_id='test:main'").fetchone()[0]
            self.assertEqual(snapshots, 1)
            self.assertEqual(deltas, 2)
            self.command("--db", db, "branch", "--campaign", "test", "--from-turn", "2", "--name", "legacy_midpoint")
            restored = self.command("--db", db, "brief", "--campaign", "test", "--action", "继续前进").stdout
            self.assertIn("王室纹章戒指", restored)

    def test_shared_universe_keeps_worlds_separate_and_lore_shared(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command(
                "--db", db, "init", "--campaign", "dockside", "--title", "Dockside Tale", "--player", "Mira",
                "--concept", "smuggler", "--location", "Harbor", "--universe", "cinder_sea", "--universe-title", "The Cinder Sea",
            )
            self.command(
                "--db", db, "init", "--campaign", "highlands", "--title", "Highland Tale", "--player", "Orin",
                "--concept", "exile", "--location", "Pass", "--universe", "cinder_sea",
            )
            self.command(
                "--db", db, "universe-lore-add", "--universe", "cinder_sea", "--title", "Ash Moon",
                "--content", "The Ash Moon turns river water silver for one night each winter.", "--constant",
            )
            worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual(worlds["active_campaign"], "highlands")
            self.assertEqual({world["id"] for world in worlds["worlds"]}, {"dockside", "highlands"})
            self.assertEqual(worlds["worlds"][0]["universe_title"], "The Cinder Sea")
            highlands = next(world for world in worlds["worlds"] if world["id"] == "highlands")
            self.assertEqual(highlands["player_state"]["location"], "Pass")
            self.assertEqual(highlands["character"]["concept"], "exile")
            self.assertEqual(highlands["turn_count"], 0)
            shared = self.command("--db", db, "brief", "--campaign", "highlands", "--action", "I watch the moon.").stdout
            self.assertIn("The Ash Moon turns river water silver", shared)
            self.command("--db", db, "select-world", "--campaign", "dockside")
            other = self.command("--db", db, "brief", "--campaign", "dockside", "--action", "I watch the moon.").stdout
            self.assertIn("The Ash Moon turns river water silver", other)
            self.assertIn("Mira", other)
            self.assertNotIn("Orin", other)

    def test_universe_index_derives_retrieval_terms_and_universe_can_be_renamed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command(
                "--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player",
                "--universe", "mirror_sea", "--universe-title", "Old Name",
            )
            self.command(
                "--db", db, "universe-lore-add", "--universe", "mirror_sea", "--title", "阿维恩王国",
                "--content", "阿维恩拥有河谷与许多自治领。", "--selective",
            )
            self.command(
                "--db", db, "universe-lore-add", "--universe", "mirror_sea", "--title", "十四主神",
                "--content", "艾芮娅受到许多治愈师敬奉。", "--selective",
            )
            self.command("--db", db, "index-universe-lore", "--universe", "mirror_sea")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我想前往阿维恩。 ").stdout
            self.assertIn("阿维恩拥有河谷", brief)
            deity_brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "我在艾芮娅神殿祈祷。 ").stdout
            self.assertIn("艾芮娅受到许多治愈师敬奉", deity_brief)
            self.command(
                "--db", db, "rename-universe", "--universe", "mirror_sea", "--title", "The Cartographer's World",
                "--description", "A living world.",
            )
            worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            renamed = next(universe for universe in worlds["universes"] if universe["id"] == "mirror_sea")
            self.assertEqual(renamed["title"], "The Cartographer's World")

    def test_schema_migrations_upgrade_legacy_tables_and_record_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "legacy.sqlite3")
            with sqlite3.connect(db) as connection:
                connection.executescript("""
                    CREATE TABLE campaign_starts (
                        campaign_id TEXT PRIMARY KEY,
                        player_name TEXT NOT NULL,
                        player_concept TEXT NOT NULL,
                        starting_location TEXT NOT NULL
                    );
                    CREATE TABLE universe_lore_entries (
                        id TEXT PRIMARY KEY,
                        universe_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        keys_json TEXT NOT NULL DEFAULT '[]',
                        secondary_keys_json TEXT NOT NULL DEFAULT '[]',
                        enabled INTEGER NOT NULL DEFAULT 1,
                        constant INTEGER NOT NULL DEFAULT 0,
                        selective INTEGER NOT NULL DEFAULT 0,
                        case_sensitive INTEGER NOT NULL DEFAULT 0,
                        insertion_order INTEGER NOT NULL DEFAULT 100,
                        priority INTEGER NOT NULL DEFAULT 50,
                        created_at TEXT NOT NULL
                    );
                """)
            with engine.connect(db) as connection:
                migrations = connection.execute(
                    "SELECT version, name FROM schema_migrations ORDER BY version"
                ).fetchall()
                start_columns = {row["name"] for row in connection.execute("PRAGMA table_info(campaign_starts)")}
                lore_columns = {row["name"] for row in connection.execute("PRAGMA table_info(universe_lore_entries)")}
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                default_universe = connection.execute(
                    "SELECT title, description FROM universes WHERE id='shattered_realms'"
                ).fetchone()
            self.assertEqual([row["version"] for row in migrations], list(range(1, engine.CURRENT_SCHEMA_VERSION + 1)))
            self.assertEqual(version, engine.CURRENT_SCHEMA_VERSION)
            self.assertIn("character_json", start_columns)
            self.assertTrue({"category", "visibility", "system_entry"}.issubset(lore_columns))
            self.assertEqual(default_universe["title"], "The Lost Lands")
            self.assertIn("several continents", default_universe["description"])
            status = json.loads(self.command("--db", db, "schema-status").stdout)
            self.assertEqual(status["current_version"], engine.CURRENT_SCHEMA_VERSION)
            self.assertEqual(len(status["migrations"]), engine.CURRENT_SCHEMA_VERSION)

    def test_lost_lands_name_migrates_without_changing_universe_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "old-world-name.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            with sqlite3.connect(db) as connection:
                connection.execute(
                    "UPDATE universes SET title='The Mirror Sea Realms', description='Old description' WHERE id='shattered_realms'"
                )
                connection.execute("DELETE FROM schema_migrations WHERE version=10")
                connection.execute("PRAGMA user_version=9")
            with engine.connect(db) as connection:
                universe = connection.execute(
                    "SELECT id, title, description FROM universes WHERE id='shattered_realms'"
                ).fetchone()
            self.assertEqual(universe["id"], "shattered_realms")
            self.assertEqual(universe["title"], "The Lost Lands")
            self.assertIn("several continents", universe["description"])

    def test_lost_lands_name_migration_preserves_a_custom_world_title(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "custom-world-name.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            with sqlite3.connect(db) as connection:
                connection.execute(
                    "UPDATE universes SET title='My Campaign Setting', description='Custom description' "
                    "WHERE id='shattered_realms'"
                )
                connection.execute("DELETE FROM schema_migrations WHERE version=10")
                connection.execute("PRAGMA user_version=9")
            with engine.connect(db) as connection:
                universe = connection.execute(
                    "SELECT title, description FROM universes WHERE id='shattered_realms'"
                ).fetchone()
            self.assertEqual(universe["title"], "My Campaign Setting")
            self.assertEqual(universe["description"], "Custom description")

    def test_retired_item_data_migration_removes_only_empty_legacy_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "legacy-items.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Mira")
            with sqlite3.connect(db) as connection:
                state = json.loads(connection.execute(
                    "SELECT state_json FROM entity_states WHERE entity_id='player'"
                ).fetchone()[0])
                state["inventory"] = []
                connection.execute("UPDATE entity_states SET state_json=? WHERE entity_id='player'",
                                   (json.dumps(state, ensure_ascii=False),))
                root = json.loads(connection.execute("SELECT snapshot_json FROM state_roots").fetchone()[0])
                root_state = json.loads(root["entity_states"][0]["state_json"])
                root_state["inventory"] = []
                root["entity_states"][0]["state_json"] = json.dumps(root_state, ensure_ascii=False)
                connection.execute("UPDATE state_roots SET snapshot_json=?", (json.dumps(root, ensure_ascii=False),))
                connection.execute(
                    """INSERT INTO universe_lore_entries
                       (id, universe_id, title, content, category, created_at)
                       VALUES ('retired-overview', 'shattered_realms', '铁剑与常见单手刃', 'old', 'Weapons', 'now')"""
                )
                connection.execute("DELETE FROM schema_migrations WHERE version=6")
                connection.execute("PRAGMA user_version=5")
            with engine.connect(db) as connection:
                current = json.loads(connection.execute(
                    "SELECT state_json FROM entity_states WHERE entity_id='player'"
                ).fetchone()[0])
                root = json.loads(connection.execute("SELECT snapshot_json FROM state_roots").fetchone()[0])
                root_state = json.loads(root["entity_states"][0]["state_json"])
                retired = connection.execute(
                    "SELECT 1 FROM universe_lore_entries WHERE id='retired-overview'"
                ).fetchone()
            self.assertNotIn("inventory", current)
            self.assertNotIn("inventory", root_state)
            self.assertIsNone(retired)

    def test_complete_database_backup_and_atomic_restore_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            backup = str(Path(directory) / "portable.sqlite3")
            self.command("--db", db, "init", "--campaign", "original", "--title", "Original", "--player", "Mira")
            self.command("--db", db, "commit", "--campaign", "original", "--manifest", str(EXAMPLE))
            backup_result = json.loads(self.command(
                "--db", db, "backup-database", "--output", backup
            ).stdout)
            self.assertEqual(backup_result["campaigns"], 1)
            self.assertEqual(backup_result["schema_version"], engine.CURRENT_SCHEMA_VERSION)
            self.command("--db", db, "init", "--campaign", "temporary", "--title", "Temporary", "--player", "Orin")
            restored = json.loads(self.command(
                "--db", db, "restore-database", "--source", backup
            ).stdout)
            self.assertTrue(restored["restored"])
            self.assertTrue(Path(restored["automatic_backup"]["path"]).is_file())
            worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual({world["id"] for world in worlds["worlds"]}, {"original"})
            timeline = json.loads(self.command(
                "--db", db, "timeline", "--campaign", "original", "--json"
            ).stdout)
            self.assertEqual(len(timeline), 1)

    def test_invalid_database_import_never_replaces_the_live_save(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            invalid = Path(directory) / "not-a-save.sqlite3"
            invalid.write_bytes(b"not a sqlite database")
            self.command("--db", db, "init", "--campaign", "safe", "--title", "Safe", "--player", "Mira")
            failed = self.command(
                "--db", db, "restore-database", "--source", str(invalid), check=False
            )
            self.assertEqual(failed.returncode, 2)
            worlds = json.loads(self.command("--db", db, "worlds", "--json").stdout)
            self.assertEqual({world["id"] for world in worlds["worlds"]}, {"safe"})

    def test_reviewable_chapter_summary_keeps_source_audit_and_stays_out_of_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            for _ in range(3):
                self.command("--db", db, "commit", "--campaign", "test", "--manifest", str(EXAMPLE))
            source = json.loads(self.command(
                "--db", db, "chapter-source", "--campaign", "test", "--start", "1", "--end", "3"
            ).stdout)
            self.assertEqual([turn["turn_number"] for turn in source["turns"]], [1, 2, 3])
            self.assertEqual(len(source["source_hash"]), 64)
            draft = json.dumps({
                "title": "戒指与后巷", "summary": "伊莲娜交出了戒指。[回合 1–3]",
                "start_turn": 1, "end_turn": 3, "status": "draft",
            }, ensure_ascii=False)
            saved = json.loads(self.command(
                "--db", db, "chapter-save", "--campaign", "test", "--chapter", draft
            ).stdout)
            self.assertEqual(saved["chapters"][0]["status"], "draft")
            self.assertTrue(saved["chapters"][0]["source_matches"])
            chapter_id = saved["chapters"][0]["id"]
            reviewed = json.loads(self.command(
                "--db", db, "chapter-update", "--campaign", "test", "--chapter", chapter_id,
                "--chapter-data", json.dumps({
                    "summary": "人工确认摘要。[回合 1–3]", "status": "approved"
                }, ensure_ascii=False),
            ).stdout)
            self.assertEqual(reviewed["chapters"][0]["status"], "approved")
            self.assertEqual(reviewed["chapters"][0]["summary"], "人工确认摘要。[回合 1–3]")
            brief = self.command("--db", db, "brief", "--campaign", "test", "--action", "继续").stdout
            self.assertNotIn("人工确认摘要", brief)
            self.command("--db", db, "restart", "--campaign", "test")
            restarted = json.loads(self.command("--db", db, "chapters", "--campaign", "test").stdout)
            self.assertEqual(restarted["chapters"], [])

    def test_turn_commit_reports_new_people_and_relationship_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            db = str(Path(directory) / "campaign.sqlite3")
            manifest = Path(directory) / "people.json"
            self.command("--db", db, "init", "--campaign", "test", "--title", "Test", "--player", "Player")
            manifest.write_text(json.dumps({
                "player_action": "我向玛拉问路。", "narration": "玛拉报上姓名，答应带你去渡口。",
                "scene": {"location": "Old Road", "present_entities": ["mara"]},
                "entities": [{"id": "mara", "type": "npc", "name": "玛拉",
                              "profile": {"role": "向导"},
                              "state": {"status": "known", "tier": "recurring", "relationship": "新认识的向导"}}],
                "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            created = json.loads(self.command(
                "--db", db, "commit", "--campaign", "test", "--manifest", str(manifest)
            ).stdout)
            self.assertEqual(created["cast_changes"][0]["kind"], "created")
            self.assertEqual(created["cast_changes"][0]["name"], "玛拉")
            manifest.write_text(json.dumps({
                "player_action": "我救了玛拉。", "narration": "玛拉认真许诺会偿还这份恩情。",
                "scene": {"location": "Old Road", "present_entities": ["mara"]}, "entities": [],
                "state_updates": [{"entity_id": "mara", "patch": {"relationship": "欠你一次救命之恩"}}],
                "events": [], "facts": [], "beliefs": [], "threads": []
            }, ensure_ascii=False), encoding="utf-8")
            updated = json.loads(self.command(
                "--db", db, "commit", "--campaign", "test", "--manifest", str(manifest)
            ).stdout)
            self.assertEqual(updated["cast_changes"][0]["kind"], "updated")
            relationship = next(
                field for field in updated["cast_changes"][0]["fields"] if field["field"] == "relationship"
            )
            self.assertEqual(relationship["before"], "新认识的向导")
            self.assertEqual(relationship["after"], "欠你一次救命之恩")


if __name__ == "__main__":
    unittest.main()
