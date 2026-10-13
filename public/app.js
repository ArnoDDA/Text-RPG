import { writingReferences, writingReferenceById } from "./writing-references.js";
import { composeTurnInput } from "./turn-input.js";

const form = document.querySelector("#action-form");
const shell = document.querySelector(".app-shell");
const homeScreen = document.querySelector("#home-screen");
const worldsScreen = document.querySelector("#worlds-screen");
const universeScreen = document.querySelector("#universe-screen");
const settingsScreen = document.querySelector("#settings-screen");
const gameScreen = document.querySelector("#game-screen");
const changeWorldButton = document.querySelector("#change-world");
const openJournalButton = document.querySelector("#open-journal");
openJournalButton.textContent = "Journey";
const openCharacterCardButton = document.querySelector("#open-character-card");
const openPartyCardButton = document.querySelector("#open-party-card");
const openMapButton = document.querySelector("#open-map");
const closeMapButton = document.querySelector("#close-map");
const gameMap = document.querySelector("#game-map");
const mapCurrentName = document.querySelector("#map-current-name");
const mapMood = document.querySelector("#map-mood");
const mapParent = document.querySelector("#map-parent");
const mapPlaceState = document.querySelector("#map-place-state");
const mapFocus = document.querySelector("#map-focus");
const mapDanger = document.querySelector("#map-danger");
const mapPlaces = document.querySelector("#map-places");
const mapRoutes = document.querySelector("#map-routes");
const closeJournalButton = document.querySelector("#close-journal");
const openManagementButton = document.querySelector("#open-management");
const backToGameButton = document.querySelector("#back-to-game");
const gameJournal = document.querySelector("#game-journal");
const journalStatus = document.querySelector("#journal-status");
const journalRecords = document.querySelector("#journal-records");
const navHomeButton = document.querySelector("#nav-home");
const navWorldsButton = document.querySelector("#nav-worlds");
const navUniverseButton = document.querySelector("#nav-universe");
const navSettingsButton = document.querySelector("#nav-settings");
const openWorldsButton = document.querySelector("#open-worlds");
const openUniverseButton = document.querySelector("#open-universe");
const openSettingsButton = document.querySelector("#open-settings");
const continueWorldButton = document.querySelector("#continue-world");
const newWorldButton = document.querySelector("#new-world");
const cancelCreateWorldButton = document.querySelector("#cancel-create-world");
const createWorldPanel = document.querySelector("#create-world-panel");
const field = document.querySelector("#action");
const speechField = document.querySelector("#speech");
const turnInputHelp = document.querySelector("#turn-input-help");
const playerQuickbar = document.querySelector("#player-quickbar");
const playerQuickbarList = document.querySelector("#player-quickbar-list");
const actionClarification = document.querySelector("#action-clarification");
const story = document.querySelector("#story");
const storyScroll = document.querySelector(".story-scroll");
const status = document.querySelector("#status");
const languageToggle = document.querySelector("#language-toggle");
const button = form.querySelector("button");
const modelSelect = document.querySelector("#model");
const worldForm = document.querySelector("#world-form");
const worldStatus = document.querySelector("#world-status");
const worldList = document.querySelector("#world-list");
const worldTrash = document.querySelector("#world-trash");
const worldTrashList = document.querySelector("#world-trash-list");
const worldTrashCount = document.querySelector("#world-trash-count");
const worldListSidebar = document.querySelector("#world-list-sidebar");
const worldTitle = document.querySelector("#world-title");
const worldPlayer = document.querySelector("#world-player");
const worldConcept = document.querySelector("#world-concept");
const worldLocation = document.querySelector("#world-location");
const worldBackground = document.querySelector("#world-background");
const worldLocationCustom = document.querySelector("#world-location-custom");
const worldLocationCustomWrap = document.querySelector("#world-location-custom-wrap");
const worldPronouns = document.querySelector("#world-pronouns");
const worldAncestry = document.querySelector("#world-ancestry");
const worldLineage = document.querySelector("#world-lineage");
const worldAppearance = document.querySelector("#world-appearance");
const worldOrigin = document.querySelector("#world-origin");
const worldOriginCustom = document.querySelector("#world-origin-custom");
const worldOriginCustomWrap = document.querySelector("#world-origin-custom-wrap");
const worldConceptCustom = document.querySelector("#world-concept-custom");
const worldConceptCustomWrap = document.querySelector("#world-concept-custom-wrap");
const worldBond = document.querySelector("#world-bond");
const worldBondCustom = document.querySelector("#world-bond-custom");
const worldBondCustomWrap = document.querySelector("#world-bond-custom-wrap");
const worldBurden = document.querySelector("#world-burden");
const worldBurdenCustom = document.querySelector("#world-burden-custom");
const worldBurdenCustomWrap = document.querySelector("#world-burden-custom-wrap");
const worldTemperament = document.querySelector("#world-temperament");
const worldOpeningPreset = document.querySelector("#world-opening-preset");
const creatorChoiceNote = document.querySelector("#creator-choice-note");
const worldSignatureItem = document.querySelector("#world-signature-item");
const worldSignatureDetail = document.querySelector("#world-signature-detail");
const characterPreviewCopy = document.querySelector("#character-preview-copy");
const characterPresetList = document.querySelector("#character-preset-list");
const presetDetailPanel = document.querySelector("#preset-detail-panel");
const presetDetailTitle = document.querySelector("#preset-detail-title");
const presetDetailContent = document.querySelector("#preset-detail-content");
const closePresetDetailButton = document.querySelector("#close-preset-detail");
const startPresetStoryButton = document.querySelector("#start-preset-story");
const worldName = document.querySelector("#world-name");
const worldMeta = document.querySelector("#world-meta");
const worldUniverseLabel = document.querySelector("#world-universe-label");
const possessionsList = document.querySelector("#possessions-list");
const possessionsTabs = document.querySelector("#possessions-tabs");
const abilityList = document.querySelector("#ability-list");
const abilityLoads = document.querySelector("#ability-loads");
const openPlayerBackpackButton = document.querySelector("#open-player-backpack");
const openPartyBackpackButton = document.querySelector("#open-party-backpack");
const consequenceList = document.createElement("div");
consequenceList.id = "character-consequences";
consequenceList.className = "character-consequences";
consequenceList.hidden = true;
abilityLoads.insertAdjacentElement("afterend", consequenceList);
const abilityRecordStatus = document.querySelector("#ability-record-status");
const possessionSuggestions = document.querySelector("#possessions-suggestions");
const resourceWalletLabel = document.querySelector("#resource-wallet-label");
const resourceBalance = document.querySelector("#resource-balance");
const tradeOffers = document.querySelector("#trade-offers");
const transactionHistory = document.querySelector("#transaction-history");
const transactionHistoryLabel = document.querySelector("#transaction-history-label");
const transactionList = document.querySelector("#transaction-list");
const possessionForm = document.querySelector("#possession-form");
const possessionId = document.querySelector("#possession-id");
const possessionName = document.querySelector("#possession-name");
const possessionCategory = document.querySelector("#possession-category");
const possessionType = document.createElement("select");
possessionType.id = "possession-type";
const possessionTypeLabel = document.createElement("label");
possessionTypeLabel.htmlFor = possessionType.id;
const possessionTypeCaption = document.createElement("span");
possessionTypeLabel.append(possessionTypeCaption, possessionType);
const suggestTypeButton = document.createElement("button");
suggestTypeButton.type = "button";
suggestTypeButton.className = "secondary";
suggestTypeButton.id = "suggest-possession-type";
const possessionTypeHint = document.createElement("small");
possessionTypeHint.id = "possession-type-hint";
possessionName.parentElement.after(possessionTypeLabel, suggestTypeButton, possessionTypeHint);
let availableItemTypes = [];
let availableItemRarities = [];
const possessionRarity = document.createElement("select");
possessionRarity.id = "possession-rarity";
const possessionRarityLabel = document.createElement("label");
possessionRarityLabel.htmlFor = possessionRarity.id;
const possessionRarityCaption = document.createElement("span");
possessionRarityLabel.append(possessionRarityCaption, possessionRarity);
possessionTypeHint.after(possessionRarityLabel);
const possessionStatus = document.querySelector("#possession-status");
const possessionDescription = document.querySelector("#possession-description");
const possessionPurpose = document.querySelector("#possession-purpose");
const possessionImportance = document.querySelector("#possession-importance");
const possessionQuantity = document.querySelector("#possession-quantity");
const possessionEquippedAs = document.querySelector("#possession-equipped-as");
const possessionResetButton = document.querySelector("#possession-reset");
const castList = document.querySelector("#cast-list");
const castForm = document.querySelector("#cast-form");
const castId = document.querySelector("#cast-id");
const castName = document.querySelector("#cast-name");
const castStatus = document.querySelector("#cast-status");
const castTier = document.querySelector("#cast-tier");
const castRole = document.querySelector("#cast-role");
const castRelationship = document.querySelector("#cast-relationship");
const castLocation = document.querySelector("#cast-location");
const castActivity = document.querySelector("#cast-activity");
const castAnchor = document.querySelector("#cast-anchor");
const castPinned = document.querySelector("#cast-pinned");
const castResetButton = document.querySelector("#cast-reset");
const partyOverviewCopy = document.querySelector("#party-overview-copy");
const partyRoster = document.querySelector("#party-roster");
function cardField(labelText, id, placeholder = "", multiline = false) {
  const label = document.createElement("label");
  label.htmlFor = id;
  label.textContent = labelText;
  const input = document.createElement(multiline ? "textarea" : "input");
  input.id = id;
  input.placeholder = placeholder;
  input.maxLength = multiline ? 900 : 600;
  if (multiline) input.rows = 2;
  label.append(input);
  return { label, input };
}

function cardEditor(form, list, title) {
  const details = document.createElement("details");
  details.className = "record-editor";
  const summary = document.createElement("summary");
  summary.textContent = title;
  form.before(details);
  details.append(summary, form);
  details.before(list);
  return details;
}

const possessionEditor = cardEditor(possessionForm, possessionsList, "Add or correct an item");
const castEditor = cardEditor(castForm, castList, "Add or correct a person");
possessionEditor.hidden = true;
castEditor.hidden = true;
const holderLabel = document.createElement("label");
holderLabel.htmlFor = "possession-holder";
holderLabel.textContent = "Held by";
const possessionHolder = document.createElement("select");
possessionHolder.id = "possession-holder";
holderLabel.append(possessionHolder);
const possessionPlace = cardField("Where, if known", "possession-place", "On your person, at an inn, with someone…");
possessionDescription.before(holderLabel, possessionPlace.label);
const castDescription = cardField("Description", "cast-description", "Appearance or enduring traits…", true);
const castVoice = cardField("Voice", "cast-voice", "How this person speaks…");
const castObjective = cardField("Current goal", "cast-objective", "What they are pursuing now…");
const castAvailability = cardField("Availability", "cast-availability", "Can they be reached or accompany you?");
const castNextMove = cardField("Next intended move", "cast-next-move", "Only if already established…");
castRole.after(castDescription.label, castVoice.label);
castActivity.parentElement.after(castObjective.label, castAvailability.label, castNextMove.label);
const homeCurrentTitle = document.querySelector("#home-current-title");
const homeCurrentMeta = document.querySelector("#home-current-meta");
const outputDensity = document.querySelector("#output-density");
const narratorProfile = document.querySelector("#narrator-profile");
const narratorPacing = document.querySelector("#narrator-pacing");
const narratorProse = document.querySelector("#narrator-prose");
const narratorSceneEnd = document.querySelector("#narrator-scene-end");
const narratorFocus = document.querySelector("#narrator-focus");
const narratorDialogue = document.querySelector("#narrator-dialogue");
const narratorAgency = document.querySelector("#narrator-agency");
const narratorNpcInitiative = document.querySelector("#narrator-npc-initiative");
const narratorMaturity = document.querySelector("#narrator-maturity");
const narratorDirectorNote = document.querySelector("#narrator-director-note");
const narratorDirectorCount = document.querySelector("#narrator-director-count");
const restoreNarratorDefaultsButton = document.querySelector("#restore-narrator-defaults");
const narratorSettingsStatus = document.querySelector("#narrator-settings-status");
const writingReferenceLibrary = document.querySelector("#writing-reference-library");
const writingReferenceStatus = document.querySelector("#writing-reference-status");
const writingLibraryCard = document.querySelector(".writing-library-card");
const writingLibraryDescription = writingLibraryCard.querySelector(".settings-card-heading p:last-child");
const writingLibraryToggle = document.createElement("button");
writingLibraryToggle.type = "button";
writingLibraryToggle.className = "quiet-button writing-library-toggle";
writingLibraryToggle.setAttribute("aria-expanded", "false");
writingLibraryToggle.textContent = "Show references";
writingLibraryCard.querySelector(".settings-card-heading").append(writingLibraryToggle);
writingLibraryDescription.hidden = true;
writingReferenceLibrary.hidden = true;
const universeBible = document.querySelector("#universe-bible");
const universeTitle = document.querySelector("#universe-title");
const universeLoreList = document.querySelector("#universe-lore-list");
const universeLoreCategories = document.querySelector("#universe-lore-categories");
const universeLoreGroups = document.querySelector("#universe-lore-groups");
const universeLoreSearch = document.querySelector("#universe-lore-search");
const universeLoreSearchStatus = document.querySelector("#universe-lore-search-status");
const sourcePreview = document.querySelector("#source-preview");
const checkpointForm = document.querySelector("#checkpoint-form");
const checkpointName = document.querySelector("#checkpoint-name");
const checkpointList = document.querySelector("#checkpoint-list");
const branchList = document.querySelector("#branch-list");
const timelineStatus = document.querySelector("#timeline-status");
const restartButton = document.querySelector("#restart");
const backupDatabaseButton = document.querySelector("#backup-database");
const exportDatabaseButton = document.querySelector("#export-database");
const importDatabaseInput = document.querySelector("#import-database");
const dataProtectionStatus = document.querySelector("#data-protection-status");
const chapterForm = document.querySelector("#chapter-form");
const chapterStart = document.querySelector("#chapter-start");
const chapterEnd = document.querySelector("#chapter-end");
const chapterStatus = document.querySelector("#chapter-status");
const chapterList = document.querySelector("#chapter-list");
const chapterSourceReview = document.querySelector("#chapter-source-review");
const chapterSourceText = document.querySelector("#chapter-source-text");
const castChangeNotice = document.querySelector("#cast-change-notice");
const castChangeList = document.querySelector("#cast-change-list");
const reviewCastChangesButton = document.querySelector("#review-cast-changes");
const loreForm = document.querySelector("#lore-form");
const loreTitle = document.querySelector("#lore-title");
const loreKeys = document.querySelector("#lore-keys");
const loreContent = document.querySelector("#lore-content");
const lorePriority = document.querySelector("#lore-priority");
const loreConstant = document.querySelector("#lore-constant");
const loreList = document.querySelector("#lore-list");
const gameTurnBadge = document.querySelector("#game-turn-badge");
const characterSheetStatus = document.querySelector("#character-sheet-status");
const gamePlayerMark = document.querySelector("#game-player-mark");
const gamePlayerName = document.querySelector("#game-player-name");
const gamePlayerDescription = document.querySelector("#game-player-description");
const gamePlayerLocation = document.querySelector("#game-player-location");
const gamePlayerCondition = document.querySelector("#game-player-condition");
const gamePlayerIdentity = document.querySelector("#game-player-identity");
const characterProfileGrid = document.querySelector("#character-profile-grid");
const attributeRecordStatus = document.querySelector("#attribute-record-status");
const gameAttributeGrid = document.querySelector("#game-attribute-grid");
const scenePhaseLabel = document.querySelector("#scene-phase-label");
const gameSceneLocation = document.querySelector("#game-scene-location");
const gameSceneObjective = document.querySelector("#game-scene-objective");
const gameSceneTurn = document.querySelector("#game-scene-turn");
const gameScenePressure = document.querySelector("#game-scene-pressure");
const journeyLocation = document.querySelector("#journey-location");
const journeySituation = document.querySelector("#journey-situation");
const journeyActivity = document.querySelector("#journey-activity");
const journeyThreat = document.querySelector("#journey-threat");
const scenePlayableContext = document.querySelector("#scene-playable-context");
const scenePlayerPosition = document.querySelector("#scene-player-position");
const sceneParticipantsSection = document.querySelector("#scene-participants-section");
const sceneParticipantsHeading = document.querySelector("#scene-participants-heading");
const sceneParticipants = document.querySelector("#scene-participants");
const sceneElementsSection = document.querySelector("#scene-elements-section");
const sceneElementsHeading = document.querySelector("#scene-elements-heading");
const sceneElements = document.querySelector("#scene-elements");
const scenePressuresSection = document.querySelector("#scene-pressures-section");
const scenePressuresHeading = document.querySelector("#scene-pressures-heading");
const scenePressures = document.querySelector("#scene-pressures");
const attributeHeading = document.querySelector(".attribute-heading");
const attributeSheetNote = document.querySelector(".character-sheet-note");
let activeWorldId = null;
let activeWorldSnapshot = null;
let lastTimelineTurns = [];
// Campaigns may differ, but they all share one fixed canon world.  The ID is
// deliberately internal: a player never needs to choose a universe.
const selectedUniverseId = "shattered_realms";
const encyclopediaGroups = Object.freeze([
  Object.freeze({
    id: "world",
    label: "World lore",
    sections: Object.freeze([
      "World overview", "Cosmos & planes", "Gods, celestials, fiends & otherworld", "Peoples & bloodlines",
      "Magic, professions & organizations", "Continents, seas & underworlds", "Nations, city-states & powers",
      "Historical ages & major events", "Monsters, dragons & supernatural phenomena", "Rumours, mysteries & forbidden lore"
    ].map((id) => Object.freeze({ id, source: "lore" })))
  }),
  Object.freeze({ id: "items", label: "Items", sections: Object.freeze([
    ["Weapons", "item-types"], ["Magic & rituals", "lore"], ["Wearables & protection", "item-types"],
    ["Tools & everyday goods", "item-types"],
    ["Travel gear & transport", "item-types"], ["Food & drink", "item-types"],
    ["Medicine & alchemy", "item-types"], ["Materials & trade", "item-types"],
    ["Treasures & relics", "item-types"]
  ].map(([id, source]) => Object.freeze({ id, source }))) }),
  Object.freeze({
    id: "guide",
    label: "Game guide",
    sections: Object.freeze([
      "Attributes & rules", "Abilities & techniques", "Magic rules", "Items & equipment"
    ].map((id) => Object.freeze({ id, source: "lore" })))
  })
]);
const encyclopediaSections = Object.freeze(encyclopediaGroups.flatMap((group) => group.sections.map((section) => section.id)));
let selectedUniverseLoreGroup = encyclopediaGroups[0].id;
let selectedUniverseLoreCategory = encyclopediaGroups[0].sections[0].id;
let selectedUniverseLoreEntryId = null;
let universeLoreQuery = "";
const collapsedUniverseLoreCategories = new Set();
const collapsedUniverseLoreSubgroups = new Set();
let expandedUniverseLoreSubgroupId = null;
let loadedUniverseLore = null;
let loadedCast = null;
let loadedPossessions = null;
let activePossessionView = "player";
let activeJournalSection = "character";
let loadedResources = null;
let loadedAbilities = null;
let loadedChapters = null;
let loadedMap = null;
let pendingPossessionSuggestions = [];
const dismissedTradeOffers = new Set();
let lastCastChanges = [];
let interfaceLanguage = localStorage.getItem("codex-rpg-language") === "zh" ? "zh" : "en";
const narratorDefaults = Object.freeze({ profile: "recommended", density: "standard", pacing: "balanced", prose: "balanced", sceneEnding: "resting", focus: "character", dialogue: "dialogue_forward", agency: "strict", npcInitiative: "active", maturity: "mature", sceneMode: "auto", recentSceneModes: [], directorNote: "" });
let sceneMode = narratorDefaults.sceneMode;
let recentSceneModes = [];
const narratorProfiles = Object.freeze({
  recommended: narratorDefaults,
  slow_burn: { ...narratorDefaults, profile: "slow_burn", density: "standard", pacing: "deliberate", prose: "atmospheric", focus: "character", dialogue: "balanced", maturity: "mature" },
  quest: { ...narratorDefaults, profile: "quest", density: "standard", pacing: "brisk", prose: "balanced", focus: "adventure", dialogue: "balanced", npcInitiative: "active" },
  intrigue: { ...narratorDefaults, profile: "intrigue", density: "standard", pacing: "balanced", prose: "balanced", focus: "intrigue", dialogue: "dialogue_forward", npcInitiative: "active" },
  romance: { ...narratorDefaults, profile: "romance", density: "standard", pacing: "deliberate", prose: "atmospheric", focus: "character", dialogue: "dialogue_forward", maturity: "mature" },
  survival: { ...narratorDefaults, profile: "survival", density: "standard", pacing: "brisk", prose: "direct", focus: "adventure", dialogue: "sparse", npcInitiative: "forceful", maturity: "intense" }
});

let characterPresets = [];
let startingAbilityCatalog = [];
let selectedCharacterPresetId = "";

const chineseText = {
  "A private story studio": "私密故事工坊", "Home": "首页", "Worlds": "世界", "World bible": "百科", "Encyclopedia": "百科", "Narrator": "叙事者", "Quick continue": "快速继续", "Model": "模型",
  "Your stories have a place to live.": "让每段故事都有归处。", "Choose where to go next. Worlds hold playable lives, the world bible holds shared history, and the narrator settings shape each new scene.": "选择下一步去向。世界保存可游玩的角色人生，世界观保存共享历史，叙事设置决定每个新场景。",
  "Continue": "继续", "No chronicle selected": "尚未选择故事", "Create a world when you are ready to begin.": "准备好时，创建一个世界。", "Continue story": "继续故事",
  "Playable lives": "可游玩的角色人生", "Create, enter, and revisit different protagonists without their memories mixing.": "创建、进入并重访不同主角，彼此的记忆不会混杂。", "Manage worlds": "管理世界",
  "Shared background": "共享背景", "Define old magic, kingdoms, faiths, factions, and rules that matter across stories.": "定义跨越故事的重要旧日魔法、王国、信仰、派系与规则。", "Open world bible": "打开百科", "World and game reference": "世界与游戏资料", "Browse the setting, its history, and the rules used while playing.": "查阅世界设定、历史，以及游玩时使用的规则。", "Open encyclopedia": "打开百科",
  "Voice and range": "语气与尺度", "Choose the available Codex model and set how dense each scene should be.": "选择可用的 Codex 模型，并设定每个场景的篇幅。", "Narrator settings": "叙事设置",
  "Each world has its own protagonist, relationships, memories, and alternate timelines.": "每个世界都有独立的主角、关系、记忆和分歧时间线。", "Create a world": "创建世界", "Create a custom story": "自定义开局", "Your worlds": "你的世界", "Your saves": "你的存档", "Reading local worlds…": "正在读取本地世界…",
  "NEW WORLD": "新世界", "Begin with a person.": "从一个人开始。", "Cancel": "取消", "A title and protagonist are enough. Background details can grow naturally through play.": "标题和主角就足够了。背景细节会在游玩中自然生长。", "World title": "世界标题", "Protagonist": "主角", "Origin": "出身", "Opening scene": "开场场景", "What is already at stake?": "一开始有什么利害关系？", "Universe and technical options": "世界观与技术选项", "Universe ID": "世界观 ID", "World ID": "世界 ID", "New universe title": "新世界观标题", "Shared universe premise": "共享世界观前提", "Enter the first scene": "进入第一幕",
  "The background behind every story.": "每个故事背后的世界。", "Shared canon is fixed outside each character’s private memories. It is the foundation every story discovers, rather than changes.": "共享设定独立于每个角色的私人记忆，并在游玩前定稿。每段故事只能发现它，而不能改写它。", "Shared canon is fixed before play. Your discoveries reveal it; they do not rewrite it.": "共享设定会在游玩前定稿。你的发现会揭示世界，而不会重写它。", "The encyclopedia is a fixed foundation shared by every world in this universe. Only entries relevant to the current scene enter the narrator’s fixed memory budget.": "百科是这个宇宙中所有世界共用的固定基础。只有与当前场景相关的条目会进入叙事者的固定记忆预算。", "The Lost Lands.": "迷失之地。", "The Lost Lands": "迷失之地", "A vast sword-and-magic world of several continents, bay regions, island routes, and lands transformed by magic.": "一个拥有多块大陆、湾区、群岛航路与魔法异域的广阔剑与魔法世界。", "A fixed reference for the one shared world behind every playable life. It gives stories a common ground without deciding what any story must become.": "所有可游玩人生共享的单一世界设定。它为故事提供共同的土壤，却不规定任何故事必须如何发展。", "CANON WORLD": "固定世界", "One world": "唯一世界", "Every campaign begins in this setting.": "每个存档都以此世界为背景。", "Fixed canon": "固定设定", "Stories discover it; they do not revise it.": "故事只能发现它，不能修改它。", "Selective memory": "按需记忆", "Only relevant entries reach the narrator.": "只有相关条目会进入叙事上下文。", "The Bible is a reference, not a global storyline. What happens in one save remains in that save.": "百科是参考资料，不是会自行推进的全球主线。一个存档中的发生之事只属于该存档。", "CANON ENCYCLOPEDIA": "设定百科", "Browse the world": "浏览世界", "Choose a chapter, then an entry. The canon stays stable while each campaign writes its own history.": "先选择章节，再选择条目。世界设定保持稳定，每个存档书写自己的历史。", "Shared background for every world in this universe.": "所有存档共用的固定世界背景。", "SELECTED UNIVERSE": "当前世界观", "World setting": "世界设定", "World bible": "世界观百科", "World overview": "世界总览", "Cosmos & planes": "宇宙与诸位面", "Gods, celestials, fiends & otherworld": "神明、天使、恶魔与异界", "Peoples & bloodlines": "种族与血统", "Magic, professions & organizations": "魔法、职业与组织", "Continents, seas & underworlds": "大陆、海域与地下世界", "Nations, city-states & powers": "国家、城邦与势力", "Historical ages & major events": "历史时代与重大事件", "Monsters, dragons & supernatural phenomena": "怪物、龙族与超自然现象", "Rumours, mysteries & forbidden lore": "传闻、未解之谜与禁忌知识", "All entries": "全部条目", "This encyclopedia is ready for its first canon entry.": "这部百科已准备好迎接第一条正式设定。", "Common knowledge": "公开常识", "Discovered in play": "游玩中发现", "Narrator reference": "叙事者参考",
  "Voice and scene range.": "叙事语气与场景尺度。", "Scene density": "场景密度", "Choose how much space a normal response gets. The story remains Chinese and character-driven.": "选择普通回复的篇幅。剧情固定为中文，并保持人物驱动。", "Narration length": "叙事长度", "Brief — a focused beat": "简短 — 聚焦一个节拍", "Standard — a complete scene": "标准 — 完整场景", "Cinematic — extended scene and dialogue": "电影感 — 延展场景与对话", "Narrative range": "叙事范围", "Mature character-driven fantasy": "成熟的角色驱动奇幻", "Privacy": "隐私",
  "RECOMMENDED DEFAULT": "推荐默认配置", "Character-led fantasy": "轻松成人角色扮演", "Balanced pacing, atmospheric prose, meaningful dialogue, strict player agency, and mature themes when they serve the story.": "平衡节奏、具体克制的文风、有意义的对话、严格的玩家自主性。日常、幽默、暧昧和成熟主题会在合适时自然出现，不会为了推进剧情强行制造危机。", "Restore defaults": "恢复默认", "Narration": "叙事", "Set the shape of each new response. Story narration remains in Simplified Chinese.": "设定每次新回复的形态。剧情叙事始终为简体中文。", "Pacing": "节奏", "Prose": "文风", "Deliberate — slow-burn scenes": "从容 — 慢热场景", "Balanced — momentum with room to breathe": "平衡 — 有推进，也留有呼吸空间", "Brisk — move toward the next turn": "明快 — 推进到下一个抉择", "Direct — clear and concrete": "直接 — 清晰而具体", "Balanced — vivid but restrained": "平衡 — 生动而克制", "Atmospheric — sensory and literary": "氛围感 — 感官且有文学性", "Story priorities": "故事重点", "These guide the narrator’s emphasis without changing established facts or taking control of your character.": "这些选项只引导叙事重点，不会更改既定事实或替你操控角色。", "Primary focus": "主要重点", "Dialogue": "对话", "Player agency": "玩家自主性", "Character — desire and relationships": "角色 — 欲望与关系", "Adventure — danger and discovery": "冒险 — 危险与发现", "Intrigue — secrets and factions": "权谋 — 秘密与派系", "Sparse — only at pressure points": "克制 — 只在压力点出现", "Balanced — dialogue and action": "平衡 — 对话与行动并重", "Dialogue-forward — character voices lead": "对话优先 — 由角色声音推动", "Strict — you decide every action": "严格 — 每个行动由你决定", "Guided — clear hooks, your decisions": "引导 — 提供清晰钩子，决定权仍在你", "Mature themes": "成熟主题", "Controls narrative emphasis only. Provider rules always remain in force.": "只控制叙事侧重；提供方规则始终有效。", "Scope": "范围", "Restrained — fade away from explicit detail": "克制 — 淡出明确细节", "Mature — story-led desire, violence, grief, ambiguity": "成熟 — 服务于故事的欲望、暴力、悲伤与暧昧", "Intense — emotionally specific when relevant": "强烈 — 相关时给予具体情绪", "Fixed foundations": "固定基础", "Chinese, limited third-person narration": "中文、受限第三人称叙事", "Canonical facts and player agency take priority": "既定事实与玩家自主性优先", "Each completed turn is saved to the local campaign ledger": "每个完成回合都会存入本地故事账本", "Recommended defaults are active.": "推荐默认配置已启用。",
  "Story profile": "故事预设", "Start from a coherent narrator preset, then fine-tune it below. Choosing a profile does not erase your director note.": "先从一组连贯的叙事预设开始，再在下方微调。选择预设不会清除导演注记。", "Preset": "预设", "Character-led fantasy — recommended": "角色驱动奇幻 — 推荐", "Slow burn — intimacy, subtext, and consequence": "慢热 — 亲密感、潜台词与后果", "Classic quest — discovery, danger, and momentum": "经典冒险 — 发现、危险与推进", "Court intrigue — secrets, leverage, and alliances": "宫廷权谋 — 秘密、筹码与结盟", "Relationship drama — dialogue and emotional tension": "关系戏剧 — 对话与情绪张力", "Grim survival — hard choices and mounting pressure": "残酷求生 — 艰难选择与持续压力", "Custom — keep my manual choices": "自定义 — 保留手动选择", "Scene ending": "场景收束", "Playable moment — hand the decision to you": "可行动时刻 — 将决定交给你", "Cliffhanger — end on a sharp turn": "悬念 — 在关键转折处收束", "Resting beat — allow a reflective landing": "停歇 — 留出反思与缓冲", "NPC initiative": "NPC 主动性", "Reactive — answer your visible choices": "被动回应 — 回应你的可见选择", "Active — independent, fact-grounded agendas": "主动 — 独立且符合事实的目标", "Forceful — frequent pressure and reversals": "强势 — 频繁压力与反转", "Director note": "导演注记", "A short persistent instruction for the current storytelling mood, theme, or immediate dramatic priority. It is included in the context preview.": "一条短的持久指令，用来设定当前的故事情绪、主题或紧迫的戏剧重点。它会出现在上下文预览中。", "Your note": "你的注记",
  "Your move": "你的行动", "Send": "发送", "Narration is in Chinese": "剧情固定为中文", "Local save": "本地存档", "Save points": "存档点", "Timeline": "时间线", "World archive": "世界档案", "Story control": "故事控制", "Key possessions": "关键持有物", "Carried & equipped": "本地存档", "Item changes from the story wait here to be recorded in the backpack.": "剧情中发生的物品变化会在这里等待记录。", "Item name": "物品名称", "Kind": "类别", "State": "状态", "Save item": "保存物品", "New": "新建", "Equipped": "已装备", "Important": "重要", "Carried": "随身", "Nothing notable is recorded yet.": "尚未记录值得注意的物品。", "World memory": "世界记忆", "Context inspector": "上下文检查器", "Preview context": "预览上下文", "Save": "保存", "Compact": "压缩", "Restart": "重开", "WRITING REFERENCE": "写作参考", "Scene calibration library": "场景写作参考库", "Two fixed original scenes: one establishes environment and world texture; the other establishes warmth and character connection. Their compact technique notes are always active; sample text never enters a turn prompt.": "两篇固定的原创场景：一篇建立环境与世界质感，另一篇建立轻松氛围与人物连接。两篇的精简技法说明始终生效，样例原文不会进入回合提示。"
};

const englishOverrides = {
  "Choose how much space a normal response gets. The story remains Chinese and character-driven.": "Choose how much space a normal response gets. The story remains Chinese and character-driven."
};

Object.assign(chineseText, {
  "Character-led fantasy — recommended": "轻松成人角色扮演 — 推荐",
  "Balanced pacing, atmospheric prose, meaningful dialogue, strict player agency, and mature themes when they serve the story.": "平衡节奏、具体克制的文风、有意义的对话、严格的玩家自主性。日常、幽默、暧昧和成熟主题会在合适时自然出现，不会为了推进剧情强行制造危机。",
  "ENCYCLOPEDIA": "百科",
  "Choose where to go next. Worlds hold playable lives, the encyclopedia holds shared lore and game reference, and the narrator settings shape each new scene.": "选择下一步去向。世界保存可游玩的角色人生，百科收录共享设定与游戏资料，叙事设置决定每个新场景。",
  "A shared reference for the setting and the rules used while playing. It gives every story a common ground without deciding what it must become.": "这里收录共同的世界设定与游玩规则，为每段故事提供基础，却不规定故事必须如何发展。",
  "Browse the encyclopedia": "浏览百科",
  "Choose a collection and chapter, search every entry, or follow links between related topics.": "先选择世界观或介绍，再浏览章节、搜索条目，或沿交叉链接查看相关内容。",
  "Name, place, faction, magic, rule, or phrase…": "名称、地点、势力、魔法、规则或任意词句……",
  "World lore": "世界观",
  "Items": "物品",
  "Weapons": "武器",
  "Wearables & protection": "穿戴与防护",
  "Armor & protection": "防具与护具",
  "Clothing & adornment": "衣着与饰品",
  "Tools & everyday goods": "工具与日用器物",
  "Travel gear & transport": "行旅装备与载具",
  "Food & drink": "食物与饮品",
  "Medicine & alchemy": "医药与炼金制品",
  "Materials & trade": "材料、货币与贸易品",
  "Treasures & relics": "珍宝与遗物",
  "Game guide": "介绍",
  "Attributes & rules": "属性与规则",
  "Abilities & techniques": "能力与技法",
  "Magic & rituals": "魔法",
  "Magic rules": "魔法与仪式",
  "Items & equipment": "物品与装备",
  "A scene library for different dramatic situations: epic arrival, warmth, travel, discovery, intrigue, dread, action, magic, intimacy, and mythic choice. Automatic matching uses one compact technique note per turn and avoids recent repeats; open any card to read its original scene.": "覆盖宏大开篇、温馨日常、行旅、探索、权谋、恐怖、冲突、魔法、亲密与神话抉择的场景参考库。自动匹配每回合只使用一条精简技法说明，并避开近期重复；展开任意卡片即可阅读原创场景。",
  "Automatic matching": "自动场景匹配",
  "Matches the current action and established situation, then avoids the two most recently used scene rhythms whenever continuity allows.": "根据当前行动和既定局面匹配场景；只要不破坏连续性，就避开最近两次使用的场景节奏。",
  "Active": "已启用",
  "Use automatic matching": "使用自动匹配",
  "Read original scene": "阅读原创场景",
  "Set for next scene": "已设为下一幕",
  "Use for next scene": "用于下一幕"
  ,"NEW CHRONICLE": "新故事"
  ,"Choose the parts that should remain true from the first page. Leave any field open when you would rather discover it in play.": "选择从第一页起就应保持真实的部分；想在游玩中探索的内容可以留空。"
  ,"1 · Chronicle": "1 · 故事"
  ,"2 · Person": "2 · 人物"
  ,"3 · History": "3 · 经历"
  ,"4 · First scene": "4 · 第一幕"
  ,"PREPARED CHARACTERS": "预设角色"
  ,"Starting characters": "开局角色"
  ,"Choose a complete life with established relationships, abilities, equipment, and a concrete opening situation.": "选择一段资料完整的人生：既有关系、能力、装备与明确的开场处境都会随角色进入存档。"
  ,"BUILT-IN STARTS": "内置预设"
  ,"Preset stories": "预设开局"
  ,"Preset stories are permanent templates. Starting one creates a separate save you may play, restart, or delete without removing the preset.": "预设是始终保留的内置模板。开始游玩后会生成一份独立存档；你可以游玩、重开或删除该存档，而不会删除预设。"
  ,"Start with this preset": "从此预设开始"
  ,"View save": "查看存档"
  ,"No preset stories are installed.": "尚未安装预设开局。"
  ,"Chronicle": "故事"
  ,"Person": "人物"
  ,"History": "经历"
  ,"First scene": "第一幕"
  ,"A save is one playable life. Its title is only for you.": "一个存档就是一段可游玩的人生；标题只供你辨认。"
  ,"Chronicle title": "故事标题"
  ,"First location": "初始地点"
  ,"Choose a known place": "选择一个已知地点"
  ,"Crown City · Old Ferry": "王冠城 · 旧渡口"
  ,"Azure Sail Port · Quiet Tower Ward": "碧帆港 · 静塔旧区"
  ,"Karad Gate · Sealed Court": "卡拉德门 · 封门庭"
  ,"Cold Harbor · White Whale Shrine": "寒港 · 白鲸祠"
  ,"Moonwell City · First Canal": "月井城 · 第一渠"
  ,"Longriver Fair · Banner Stone": "长河集 · 盟旗石"
  ,"Deerbell Fair · Empty Fields": "鹿铃集 · 空田"
  ,"Windward Port · Homecoming Stele": "风帆港 · 归帆碑"
  ,"Twinlamp City · Greyshore Archive": "双灯城 · 灰岸档案室"
  ,"Somewhere else — write it myself": "其他地点 — 自行填写"
  ,"The person": "这个人"
  ,"Name a person first; ancestry and appearance are story facts, never limits.": "先定义一个人；种族与外貌是故事事实，而不是限制。"
  ,"Name": "姓名"
  ,"Pronouns / address": "代词／称呼"
  ,"Ancestry": "种族"
  ,"Unspecified — discover in play": "暂不设定 — 在游玩中发现"
  ,"Other / write your own": "其他／自行填写"
  ,"Human": "人类"
  ,"Elf": "精灵"
  ,"Dwarf": "矮人"
  ,"Halfling": "半身人"
  ,"Gnome": "侏儒"
  ,"Orc": "兽人"
  ,"Goblin": "地精"
  ,"Dragonborn": "龙裔"
  ,"Tiefling": "提夫林"
  ,"Aasimar": "亚斯玛"
  ,"Lineage or heritage": "血统或传承"
  ,"Defining appearance": "显著外貌"
  ,"Life before the first page": "故事开始之前"
  ,"Pick a familiar footing in this world. Each choice is a beginning, not a class or a rule.": "选择角色在这个世界中的生活起点。每项选择只是过去的一部分，不是职业或规则限制。"
  ,"These become durable character knowledge. They give the narrator material without choosing your future.": "这些会成为长期角色资料，为叙事提供素材，但不替你决定未来。"
  ,"Origin": "出身"
  ,"Calling": "身份／职业"
  ,"Leave open — discover in play": "暂时留空 — 在游玩中发现"
  ,"River toll household": "河税与渡口人家"
  ,"Port trader or sailor family": "港口商队或船员家庭"
  ,"Stonegate workshop or mining community": "石门工坊或矿脉社区"
  ,"Temple, school, or scriptorium": "神殿、学舍或抄写院"
  ,"Forest village or travelling camp": "林径村落或游牧营地"
  ,"Minor nobility, office, or embassy": "小贵族、官署或使团"
  ,"Write my own": "自行填写"
  ,"Roadbound adventurer": "漂泊冒险者"
  ,"Hired guard or former soldier": "雇佣护卫或老兵"
  ,"Apprentice mage, priest, or healer": "学徒法师、司祭或医师"
  ,"Guide, courier, or sailor": "向导、信使或船员"
  ,"Trader, craftsperson, or scribe": "商人、工匠或抄写员"
  ,"Court attendant, agent, or negotiator": "贵族侍从、密探或谈判者"
  ,"A bond": "重要牵绊"
  ,"A burden": "随身负担"
  ,"First impression": "给人的第一印象"
  ,"None fixed yet": "尚未固定"
  ,"Family or chosen family": "家人或选择的家人"
  ,"A former mentor, school, or faith": "旧导师、师门或教团"
  ,"Comrades, a crew, or an employer": "同袍、船员或雇主"
  ,"A home place or community": "故乡的一处土地或社区"
  ,"Someone who owes you": "欠你人情的人"
  ,"None declared": "尚未声明"
  ,"An unpaid debt": "未还的债务"
  ,"An unkept oath": "尚未履行的誓言"
  ,"A concealed identity or lineage": "被隐瞒的身份或血统"
  ,"Someone missing whom you seek": "正在追查的失踪之人"
  ,"The cost of a past failure": "一次失败留下的后果"
  ,"Let it emerge in play": "在游玩中呈现"
  ,"Reserved and observant": "克制而善于观察"
  ,"Frank and hard to move": "坦率而难以退让"
  ,"Quick, polite, difficult to read": "机敏、礼貌、难以看透"
  ,"Warm-hearted, impatient with authority": "热心，却对权威不耐烦"
  ,"Composed, always counts the cost": "沉着，习惯先衡量代价"
  ,"The first scene": "第一幕"
  ,"Choose an immediate reason to act; change any wording after the selection.": "选择一个立即行动的理由；选中后仍可修改措辞。"
  ,"Opening pressure": "开场压力"
  ,"Leave open — begin quietly": "暂时留空 — 平静开始"
  ,"A missing recipient": "失踪的收信人"
  ,"A debt calls you back": "旧债召你归来"
  ,"A trail goes wrong": "线索走向意外"
  ,"A commission with a hidden term": "隐瞒条件的委托"
  ,"A name from the past": "旧日名字重现"
  ,"An ordinary thing goes wrong": "日常秩序出了问题"
  ,"Set the immediate pressure. It opens the story; it does not predetermine its path.": "设定眼前的压力。它打开故事，而不预先决定故事走向。"
  ,"What has brought you here?": "是什么把你带到这里？"
  ,"A significant possession": "一件重要持有物"
  ,"optional": "可选"
  ,"Why it matters": "它为何重要"
  ,"OPENING RECORD": "开局记录"
  ,"A life waiting for its first decisive moment.": "一段人生，正等待第一个决定性的时刻。"
  ,"This person enters the story as": "这个人将以如下身份进入故事："
  ,"Begin the first scene": "进入第一幕"
  ,"The Ashes of a Crown": "王冠的余烬"
  ,"The western gate of Aurel": "奥雷尔的西门"
  ,"Your character’s name": "角色姓名"
  ,"she/her · captain · whatever fits": "她／她 · 队长 · 任何适合的称呼"
  ,"Ashen elf of the river courts": "河廷灰烬精灵"
  ,"A habit, scar, bearing, or detail people notice": "一个习惯、伤疤、姿态，或他人会注意到的细节"
  ,"Raised above a ferry house on the Salt Road": "在盐路上一座渡口屋的楼上长大"
  ,"A court scribe who learned to fight": "学会战斗的宫廷抄写员"
  ,"Someone, somewhere, or something you cannot abandon": "一个你无法抛下的人、地方或事物"
  ,"A debt, secret, oath, pursuit, or loss": "债务、秘密、誓言、追捕或失去之物"
  ,"How strangers tend to read you": "陌生人通常如何看待你"
  ,"A secret, promise, pursuit, opportunity, or danger that matters on the first day.": "一个会在第一天就产生影响的秘密、承诺、追捕、机会或危险。"
  ,"The brass key from my mother": "母亲留下的黄铜钥匙"
  ,"What is known, suspected, or owed because of it": "人们已知、怀疑或因此欠下的是什么"
  ,"Cast & party": "人物与队伍"
  ,"Local continuity": "本地延续"
  ,"Important people are stored with this timeline. Party members and pinned people stay available to the narrator without loading every person you have met.": "重要人物会随此时间线保存。队伍成员和置顶人物会持续提供给叙事者，不会加载你遇到过的所有人。"
  ,"Important people are stored with this timeline. Party members, core people, and pinned people stay available to the narrator without loading every person you have met.": "重要人物会随此时间线保存。队伍成员、核心人物和置顶人物会持续提供给叙事者，不会加载你遇到过的所有人。"
  ,"Name or the name they use": "姓名或常用称呼"
  ,"Place in your story": "在故事中的位置"
  ,"Party member": "队伍成员"
  ,"Core person": "核心人物"
  ,"Known person": "已知人物"
  ,"Away / separated": "离队／分离"
  ,"Archive": "归档"
  ,"Dead": "已死亡"
  ,"Continuity tier": "延续层级"
  ,"Core": "核心"
  ,"Recurring": "常驻"
  ,"Background": "背景"
  ,"Role: scout, sister, ship captain…": "身份：斥候、姐姐、船长……"
  ,"Relationship to you": "与你的关系"
  ,"Current location": "当前位置"
  ,"Current activity": "当前活动"
  ,"What must not be forgotten about this person or your bond": "这个人或你们之间绝不能忘记的事"
  ,"Keep in the active continuity set": "持续保留在核心记忆中"
  ,"Save person": "保存人物"
  ,"Party": "队伍"
  ,"Core people": "核心人物"
  ,"Known people": "已知人物"
  ,"Away": "离队"
  ,"No important people are recorded yet. Named people who become significant are saved here with the campaign.": "尚未记录重要人物。成为故事关键的具名人物会与存档一起保留在这里。"
  ,"Remembered:": "记得："
  ,"Person saved in this local timeline.": "人物已保存到当前本地时间线。"
  ,"Could not read cast.": "无法读取人物档案。"
  ,"Could not save person.": "无法保存人物。"
  ,"LOCAL CONTINUITY UPDATED": "本地人物记录已更新"
  ,"People remembered after this scene": "这一幕后记住的人物变化"
  ,"Review people": "查看人物"
  ,"Save protection": "存档保护"
  ,"Back up locally, download a portable copy, or restore a complete Secret Fire database.": "可在本机备份、下载便携副本，或恢复完整的 Secret Fire 数据库。"
  ,"Back up now": "立即备份"
  ,"Export": "导出"
  ,"Import": "导入"
  ,"Imports are checked and migrated before replacing the live save.": "导入文件会先经过校验与迁移，再替换当前存档。"
  ,"Choose a chapter, search every entry, or follow links between related places, people, and powers.": "选择章节、搜索全部条目，或沿交叉链接查看相关地点、人物与势力。"
  ,"Search the encyclopedia": "搜索百科"
  ,"Name, place, faction, magic, or phrase…": "名称、地点、势力、魔法或任意词句……"
  ,"Chapter summaries": "章节摘要"
  ,"Reviewable": "可审核"
  ,"Create a draft from exact story turns, edit it, then approve it. Summaries remain reading aids and never replace or alter the original story.": "从准确的故事回合生成草稿，编辑后再确认。摘要只用于阅读，绝不会替代或改写原始故事。"
  ,"From turn": "起始回合"
  ,"Through turn": "结束回合"
  ,"Generate draft": "生成草稿"
  ,"Play at least one story turn to create a chapter.": "至少完成一个故事回合后才能创建章节。"
  ,"Source turns": "来源回合"
  ,"ADVENTURE JOURNAL": "冒险日志"
  ,"Character & story": "角色与故事"
  ,"Your protagonist, current situation, possessions, people, and local save.": "查看主角、当前局势、持有物、人物关系与本地存档。"
  ,"Character": "角色"
  ,"Test profile": "测试档案"
  ,"Test character": "测试角色"
  ,"An empty character prepared for interface testing.": "一个用于检查游戏界面的空白角色。"
  ,"Location": "位置"
  ,"Condition": "状态"
  ,"Identity": "身份"
  ,"Not set": "未设定"
  ,"Unrecorded": "未记录"
  ,"Seven attributes": "七项属性"
  ,"Not assigned": "未分配"
  ,"Physique": "体魄"
  ,"Agility": "灵巧"
  ,"Perception": "感知"
  ,"Intellect": "智识"
  ,"Will": "意志"
  ,"Charisma": "魅力"
  ,"Mystic power": "神秘"
  ,"Attributes will appear here after the action system is connected. Empty values do not limit free play yet.": "行动系统接入后，属性会显示在这里；当前空值不会限制自由游玩。"
  ,"Abilities": "能力"
  ,"None recorded": "尚无记录"
  ,"No special abilities are recorded yet. Ordinary actions still use attributes, training, and real conditions.": "尚未掌握已记录的特殊能力；普通行动仍可依靠属性、专业与现实条件进行。"
  ,"Current scene": "当前场景"
  ,"Opening": "开场"
  ,"No location selected": "尚未选择地点"
  ,"The first situation has not been established.": "第一幕尚未建立明确局势。"
  ,"Turn 0": "第 0 回合"
  ,"No active pressure": "暂无明确压力"
  ,"Blank test character": "空白测试角色"
  ,"Only the minimum needed to enter the game; everything else stays open.": "只填写进入游戏所需内容，其余设定全部留空。"
  ,"Use this character": "使用此角色"
  ,"FIRST SCENE": "第一幕"
  ,"The story is waiting for your first move.": "故事正在等待你的第一个行动。"
  ,"There is no fixed opening pressure. You may begin quietly, observe, speak, or act.": "这里没有预设的开场压力。你可以安静地开始，也可以观察、交谈或行动。"
  ,"Observe the surroundings": "观察周围环境"
  ,"Check what I carry": "检查随身物品"
  ,"Look for someone to speak with": "寻找可以交谈的人"
  ,"First move": "初次行动"
  ,"Profile ready": "档案已就绪"
  ,"Profile open": "档案待补充"
  ,"Assigned": "已记录"
  ,"Normal": "状态正常"
  ,"No declared identity": "身份尚未设定"
  ,"First scene has no fixed objective yet.": "第一幕尚未设定明确目标。"
  ,"Waiting for your first move": "等待你的第一个行动"
  ,"Journal": "手记"
  ,"Manage": "管理"
  ,"FIELD NOTES": "旅途手记"
  ,"Close journal": "关闭手记"
  ,"Character card": "角色卡"
  ,"Life and ties": "经历与关系"
  ,"Profile": "人物资料"
  ,"Active party": "当前小队"
  ,"The party is the group that can travel and act with you now. Other people stay in the wider cast without crowding the active roster.": "小队是当前可以与你同行、行动的成员；其他重要人物仍保留在人物档案中，不会挤占当前队伍。"
  ,"Possessions": "持有物"
  ,"People": "人物"
  ,"No possessions recorded yet.": "尚无持有物记录。"
  ,"No people recorded yet.": "尚无人物记录。"
  ,"CHRONICLE MANAGEMENT": "故事管理"
  ,"Manage this story": "管理这段故事"
  ,"Save points, chapter summaries, and backup tools live here, away from play.": "存档点、章节摘要与备份功能集中在这里，不打断游玩。"
  ,"Name this moment": "为这一刻命名"
  ,"Before I open the door": "打开门之前"
  ,"Timelines": "时间线"
  ,"← Back to story": "← 返回故事"
  ,"A story begins here.": "故事由此开始。"
  ,"The first step is yours to decide.": "接下来的一步，由你决定。"
  ,"Write what you do, say, or notice below. There are no fixed choices.": "在下方写下你做什么、说什么，或注意到了什么；没有固定选项。"
  ,"People in your story were updated.": "故事中的人物记录已更新。"
  ,"Open journal": "打开手记"
  ,"Write what you attempt, say, or observe…": "写下你尝试做什么、说什么，或观察什么……"
  ,"How this turn was understood": "本回合的行动理解"
  ,"Stopped at:": "推进至："
  ,"Recently removed": "最近删除"
  ,"Removed stories can be restored with all their turns, saves, people, and items.": "删除的故事仍保留所有剧情、存档点、人物和物品，可在这里恢复。"
  ,"Delete story": "删除存档"
  ,"Restore": "恢复"
  ,"Permanently delete": "永久删除"
  ,"YOUR JOURNEY": "旅途"
  ,"Journey": "旅途"
  ,"Journey sections": "旅途栏目"
  ,"Backpack": "背包"
  ,"Party": "小队"
  ,"Backpack & equipment": "背包与装备"
  ,"Party & people": "小队与人物"
  ,"Map": "地图"
  ,"Journey map": "旅途地图"
  ,"Close map": "关闭地图"
  ,"DISCOVERED PLACES": "已发现的地点"
  ,"Places established in this save remain here after you leave. Lines show journeys actually taken, not every possible road.": "已经在这个存档中成立的地点，离开后仍会保留。路线只代表实际走过的旅程，不代表所有可通行道路。"
  ,"Within": "所属地点"
  ,"Last known state": "最后状态"
  ,"Not yet established": "尚未明确"
  ,"No lasting change recorded": "没有已记录的长期变化"
  ,"CURRENT PLACE": "当前地点"
  ,"Everyday life": "日常侧重"
  ,"Risk": "风险特征"
  ,"Places reached": "已到达"
  ,"Journeys taken": "走过的路线"
  ,"Reading location…": "正在读取地点……"
  ,"Action": "行为"
  ,"Speech": "说话"
  ,"Describe what you try; leave the result open.": "写下你尝试做的事，结果交给故事。"
  ,"Your character's exact words, if any.": "如果要说话，请写角色的原话。"
  ,"I step closer to the door and listen before opening it…": "我走近门口，先贴着门听一听……"
  ,"I heard someone inside. Who is there?": "我听见里面有人。谁在那儿？"
  ,"Write an action, speech, or both. Neither needs a preset category.": "行为和说话可以只填一个，也可以都填；不用选类别。"
  ,"Edit": "编辑"
  ,"Equip": "装备"
  ,"Unequip": "卸下"
  ,"Store": "存放"
  ,"Carry": "携带"
  ,"Join party": "加入小队"
  ,"Leave party": "离开小队"
  ,"Add or correct an item": "添加或修正物品"
  ,"Add or correct a person": "添加或修正人物"
  ,"Held by": "由谁持有"
  ,"Where, if known": "所在地点（如已知）"
  ,"Description": "外观与特征"
  ,"Voice": "说话方式"
  ,"Current goal": "当前目标"
  ,"Availability": "是否可以同行／联系"
  ,"Next intended move": "下一步打算"
  ,"Equipped": "已装备"
  ,"Important": "重要物品"
  ,"Carried": "随身物品"
  ,"Elsewhere": "不在身边"
  ,"Stored": "已存放"
  ,"Given away": "已交出"
  ,"adventurer": "冒险者"
  ,"Enter world": "进入故事"
  ,"Create your first chronicle, or return to one below.": "创建第一个故事，或继续已有故事。"
  ,"Ready when you are.": "随时可以继续。"
  ,"Ready to begin.": "已经准备好。"
  ,"The room is waiting for your answer.": "酒馆里的人都在等你的回答。"
  ,"Narrator model is fixed for this local session.": "当前本地会话已固定叙事模型。"
  ,"The narrator model is fixed by the local launch setting.": "叙事模型由本地启动设置固定。"
  ,"These settings affect how Codex presents the next turn. The model menu contains only models available to the signed-in local account.": "这些设置决定下一回合的叙事方式，并从下一幕开始生效。"
  ,"Your campaign ledger lives locally. Each new turn is sent through the signed-in local Codex session to obtain narration; the game does not save an API key.": "故事记录保存在本机。每个新回合会通过当前登录的本地会话生成叙事；游戏不会保存 API 密钥。"
  ,"Show references": "展开写作参考"
  ,"Hide references": "收起写作参考"
  ,"Unnamed character": "未命名角色"
  ,"Unspecified calling": "身份待定"
  ,"Unknown location": "地点未明"
  ,"CURRENT SCENE": "当前场景"
  ,"Character card": "玩家信息卡"
  ,"Party card": "小队信息卡"
  ,"Open player backpack": "打开玩家背包"
  ,"Open party backpack": "打开小队背包"
  ,"Quick items": "快捷物品"
  ,"Player backpack": "玩家背包"
  ,"No carried items to reference yet": "还没有可快速引用的随身物品"
});

function applyStaticLanguage() {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const source = node.__localeSource ?? node.nodeValue;
    node.__localeSource = source;
    const trimmed = source.trim();
    const translated = interfaceLanguage === "zh" ? chineseText[trimmed] : englishOverrides[trimmed];
    node.nodeValue = translated ? source.replace(trimmed, translated) : source;
  }
  for (const element of document.querySelectorAll("[placeholder]")) {
    const source = element.dataset.localePlaceholder ?? element.getAttribute("placeholder");
    element.dataset.localePlaceholder = source;
    element.setAttribute("placeholder", interfaceLanguage === "zh" ? (chineseText[source] ?? source) : source);
  }
}

function applyLanguage() {
  shell.dataset.language = interfaceLanguage;
  document.documentElement.lang = interfaceLanguage === "zh" ? "zh-CN" : "en";
  languageToggle.setAttribute("aria-label", interfaceLanguage === "zh" ? "切换系统界面语言" : "Switch interface language");
  writingLibraryToggle.textContent = localized(writingLibraryToggle.getAttribute("aria-expanded") === "true" ? "Hide references" : "Show references");
  applyStaticLanguage();
  const narratorIntro = document.querySelector(".settings-intro > div > p:not(.card-kicker)");
  if (narratorIntro) narratorIntro.textContent = interfaceLanguage === "zh"
    ? "角色关系、日常生活、幽默、暧昧和成熟主题会自然展开。叙事者不会为了推进故事凭空制造危机。改动只保存在本机，并从下一幕开始生效。"
    : "Character chemistry, daily life, humor, flirtation, and mature themes can unfold naturally. The narrator does not manufacture a crisis just to move the story. Changes save locally and apply to the next scene.";
  possessionCategory.parentElement.childNodes[0].nodeValue = interfaceLanguage === "zh" ? "记录用途" : "Record role";
  possessionTypeCaption.textContent = interfaceLanguage === "zh" ? "基础类别（决定物品的归属）" : "Base category (what this item is)";
  possessionRarityCaption.textContent = interfaceLanguage === "zh" ? "鉴定状态与等级（不等于战力）" : "Identification and rarity (not power)";
  suggestTypeButton.textContent = interfaceLanguage === "zh" ? "根据名称与描述建议" : "Suggest from name and description";
  openCharacterCardButton.textContent = localized("Character card");
  openPartyCardButton.textContent = localized("Party card");
  openPlayerBackpackButton.textContent = `${localized("Open player backpack")} →`;
  openPartyBackpackButton.textContent = `${localized("Open party backpack")} →`;
  playerQuickbar.querySelector("summary span").textContent = localized("Quick items");
  playerQuickbar.querySelector("summary .summary-hint").textContent = localized("Player backpack");
  if (turnInputHelp.classList.contains("input-warning")) {
    turnInputHelp.textContent = interfaceLanguage === "zh" ? "请至少填写行为或说话。" : "Write an action or speech before sending.";
  }
  renderWritingReferenceLibrary();
  updateCharacterPreview();
  if (loadedUniverseLore) renderUniverseLore(loadedUniverseLore);
  if (loadedCast) renderCast(loadedCast);
  if (loadedPossessions) renderPossessions(loadedPossessions);
  if (loadedResources) renderResources(loadedResources);
  if (loadedAbilities) renderAbilities(loadedAbilities);
  if (loadedChapters) renderChapters(loadedChapters);
  if (loadedMap && !gameMap.hidden) renderMap(loadedMap);
  renderCastChanges(lastCastChanges);
  if (activeWorldSnapshot) {
    renderGameOverview(activeWorldSnapshot);
    if (!lastTimelineTurns.length) renderEmptyStory(activeWorldSnapshot);
  }
}

writingLibraryToggle.addEventListener("click", () => {
  const expanded = writingLibraryToggle.getAttribute("aria-expanded") !== "true";
  writingLibraryToggle.setAttribute("aria-expanded", String(expanded));
  writingLibraryDescription.hidden = !expanded;
  writingReferenceLibrary.hidden = !expanded;
  writingLibraryToggle.textContent = localized(expanded ? "Hide references" : "Show references");
});

function localized(value) {
  return interfaceLanguage === "zh" ? (chineseText[value] ?? value) : value;
}

function displayValue(value, fallback) {
  const text = String(value ?? "").trim();
  return text && text.toLowerCase() !== "null" ? text : localized(fallback);
}

function narratorSettingsPayload() {
  return {
    pacing: narratorPacing.value,
    prose: narratorProse.value,
    focus: narratorFocus.value,
    dialogue: narratorDialogue.value,
    agency: narratorAgency.value,
    sceneEnding: narratorSceneEnd.value,
    npcInitiative: narratorNpcInitiative.value,
    maturity: narratorMaturity.value,
    sceneMode,
    recentSceneModes,
    directorNote: narratorDirectorNote.value.trim()
  };
}

function writeNarratorSettings(settings) {
  const next = { ...narratorDefaults, ...settings };
  narratorProfile.value = narratorProfiles[next.profile] ? next.profile : "custom";
  outputDensity.value = next.density;
  narratorPacing.value = next.pacing;
  narratorProse.value = next.prose;
  narratorSceneEnd.value = next.sceneEnding;
  narratorFocus.value = next.focus;
  narratorDialogue.value = next.dialogue;
  narratorAgency.value = next.agency;
  narratorNpcInitiative.value = next.npcInitiative;
  narratorMaturity.value = next.maturity;
  narratorDirectorNote.value = next.directorNote;
  sceneMode = writingReferenceById[next.sceneMode] ? next.sceneMode : "auto";
  recentSceneModes = Array.isArray(next.recentSceneModes) ? next.recentSceneModes.filter((id) => writingReferenceById[id]).slice(-2) : [];
  renderWritingReferenceLibrary();
  updateDirectorCount();
}

function loadNarratorSettings() {
  try {
    const saved = JSON.parse(localStorage.getItem("codex-rpg-narrator-settings") || "null");
    const migrated = saved && typeof saved === "object" ? { ...saved } : { density: localStorage.getItem("codex-rpg-output-density") ?? narratorDefaults.density };
    if (migrated.profile === "recommended" && migrated.dialogue === "balanced") migrated.dialogue = "dialogue_forward";
    const legacyRecommended = migrated.profile === "recommended"
      && migrated.pacing === "balanced"
      && migrated.prose === "atmospheric"
      && migrated.sceneEnding === "open_action"
      && migrated.focus === "character"
      && migrated.dialogue === "dialogue_forward"
      && migrated.agency === "strict"
      && migrated.npcInitiative === "active"
      && migrated.maturity === "mature"
      && !String(migrated.directorNote || "").trim();
    if (legacyRecommended) {
      Object.assign(migrated, { prose: "balanced", sceneEnding: "resting", npcInitiative: "active" });
      localStorage.setItem("codex-rpg-narrator-settings", JSON.stringify(migrated));
    }
    const passiveRecommended = migrated.profile === "recommended"
      && migrated.pacing === "balanced"
      && migrated.prose === "balanced"
      && migrated.sceneEnding === "resting"
      && migrated.focus === "character"
      && migrated.dialogue === "dialogue_forward"
      && migrated.agency === "strict"
      && migrated.npcInitiative === "reactive"
      && migrated.maturity === "mature"
      && !String(migrated.directorNote || "").trim();
    if (passiveRecommended) {
      migrated.npcInitiative = "active";
      localStorage.setItem("codex-rpg-narrator-settings", JSON.stringify(migrated));
    }
    writeNarratorSettings(migrated);
  } catch {
    writeNarratorSettings(narratorDefaults);
  }
}

function saveNarratorSettings() {
  const settings = { profile: narratorProfile.value, density: outputDensity.value, ...narratorSettingsPayload() };
  localStorage.setItem("codex-rpg-narrator-settings", JSON.stringify(settings));
  localStorage.setItem("codex-rpg-output-density", settings.density);
  narratorSettingsStatus.textContent = interfaceLanguage === "zh" ? "已保存到本机；这些选择会从下一幕开始生效。" : "Saved locally. These choices apply to the next scene.";
}

function updateDirectorCount() {
  narratorDirectorCount.textContent = `${narratorDirectorNote.value.length} / 600`;
}

function renderWritingReferenceLibrary() {
  const automatic = sceneMode === "auto";
  const selected = writingReferenceById[sceneMode];
  writingReferenceStatus.textContent = automatic
    ? (interfaceLanguage === "zh" ? "自动匹配 · 避开最近两种场景" : "Automatic · avoids recent repeats")
    : (interfaceLanguage === "zh" ? `下一幕：${selected.zhLabel}` : `Next scene: ${selected.label}`);
  writingReferenceLibrary.replaceChildren();
  const auto = document.createElement("article");
  auto.className = `writing-reference writing-reference-auto${automatic ? " active" : ""}`;
  const autoHeading = document.createElement("div");
  const autoTitle = document.createElement("h3");
  autoTitle.textContent = localized("Automatic matching");
  const autoChinese = document.createElement("span");
  autoChinese.textContent = "自动场景匹配";
  autoHeading.append(autoTitle, autoChinese);
  const autoSummary = document.createElement("p");
  autoSummary.textContent = localized("Matches the current action and established situation, then avoids the two most recently used scene rhythms whenever continuity allows.");
  const autoButton = document.createElement("button");
  autoButton.type = "button";
  autoButton.textContent = localized(automatic ? "Active" : "Use automatic matching");
  autoButton.disabled = automatic;
  autoButton.addEventListener("click", () => {
    sceneMode = "auto";
    renderWritingReferenceLibrary();
    saveNarratorSettings();
  });
  auto.append(autoHeading, autoSummary, autoButton);
  writingReferenceLibrary.append(auto);
  for (const reference of writingReferences) {
    const card = document.createElement("article");
    card.className = `writing-reference${reference.id === sceneMode ? " active" : ""}`;
    const heading = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = reference.label;
    const chinese = document.createElement("span");
    chinese.textContent = reference.zhLabel;
    heading.append(title, chinese);
    const summary = document.createElement("p");
    summary.textContent = reference.summary;
    const sampleDetails = document.createElement("details");
    const sampleToggle = document.createElement("summary");
    sampleToggle.textContent = localized("Read original scene");
    const sample = document.createElement("blockquote");
    sample.textContent = reference.sample;
    sampleDetails.append(sampleToggle, sample);
    const select = document.createElement("button");
    select.type = "button";
    select.textContent = localized(reference.id === sceneMode ? "Set for next scene" : "Use for next scene");
    select.disabled = reference.id === sceneMode;
    select.addEventListener("click", () => {
      sceneMode = reference.id;
      renderWritingReferenceLibrary();
      saveNarratorSettings();
    });
    card.append(heading, summary, sampleDetails, select);
    writingReferenceLibrary.append(card);
  }
}

function append(kind, text, shouldScroll = true) {
  const article = document.createElement("article");
  article.className = kind;
  article.textContent = text;
  story.append(article);
  if (shouldScroll) article.scrollIntoView({ behavior: "smooth", block: "end" });
  return article;
}

function appendTurnPending() {
  const article = document.createElement("article");
  article.className = "turn-pending";
  article.setAttribute("role", "status");
  article.setAttribute("aria-live", "polite");
  const line = document.createElement("div");
  line.className = "turn-pending-line";
  const pulse = document.createElement("span");
  pulse.className = "turn-pending-pulse";
  pulse.setAttribute("aria-hidden", "true");
  const message = document.createElement("span");
  message.className = "turn-pending-message";
  line.append(pulse, message);
  const elapsed = document.createElement("small");
  elapsed.className = "turn-pending-elapsed";
  article.append(line, elapsed);
  story.append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });

  const started = Date.now();
  const stages = interfaceLanguage === "zh"
    ? ["正在读取当前场景", "正在理解你的行动", "正在核对行动结果", "正在生成这一幕", "正在保存到故事"]
    : ["Reading the current scene", "Understanding your action", "Checking the outcome", "Writing this scene", "Saving the turn"];
  const render = () => {
    const seconds = Math.floor((Date.now() - started) / 1000);
    const stage = stages[Math.min(Math.floor(seconds / 18), stages.length - 1)];
    const clock = interfaceLanguage === "zh"
      ? `已等待 ${seconds < 60 ? `${seconds} 秒` : `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`}`
      : `Waiting ${seconds < 60 ? `${seconds}s` : `${Math.floor(seconds / 60)}m ${seconds % 60}s`}`;
    message.textContent = `${stage}…`;
    elapsed.textContent = clock;
    status.textContent = `${stage}… ${clock}`;
  };
  render();
  const timer = window.setInterval(render, 1000);
  return {
    article,
    stop() {
      window.clearInterval(timer);
      article.remove();
    }
  };
}

function appendActionReading(frame) {
  if (!frame || frame.mode !== "play") return;
  const details = document.createElement("details");
  details.className = "action-reading";
  const summary = document.createElement("summary");
  summary.textContent = interfaceLanguage === "zh" ? "行动计划" : "Action plan";
  const interpretation = document.createElement("p");
  interpretation.textContent = frame.interpretation;
  const boundary = document.createElement("small");
  boundary.textContent = `${localized("Stopped at:")} ${frame.first_boundary}`;
  details.append(summary, interpretation, boundary);
  const rows = [
    [interfaceLanguage === "zh" ? "目标" : "Goal", frame.goal],
    [interfaceLanguage === "zh" ? "对象" : "Target", frame.target],
    [interfaceLanguage === "zh" ? "方法" : "Method", frame.method],
    [interfaceLanguage === "zh" ? "风险取向" : "Risk", frame.risk_tolerance]
  ].filter(([, value]) => String(value ?? "").trim());
  const orders = Array.isArray(frame.party_orders) ? frame.party_orders : [];
  if (orders.length) {
    rows.push([
      interfaceLanguage === "zh" ? "小队分工" : "Party orders",
      orders.map((item) => `${item.role}: ${item.instruction}`).join("；")
    ]);
  }
  const refs = [
    ...(Array.isArray(frame.ability_refs) && frame.ability_refs.length ? [interfaceLanguage === "zh" ? `能力 ${frame.ability_refs.join("、")}` : `Abilities ${frame.ability_refs.join(", ")}`] : []),
    ...(Array.isArray(frame.item_refs) && frame.item_refs.length ? [interfaceLanguage === "zh" ? `装备 ${frame.item_refs.join("、")}` : `Items ${frame.item_refs.join(", ")}`] : [])
  ];
  if (refs.length) rows.push([interfaceLanguage === "zh" ? "调用" : "References", refs.join("；")]);
  if (rows.length) {
    const grid = document.createElement("dl");
    grid.className = "action-plan-grid";
    for (const [label, value] of rows) {
      const term = document.createElement("dt");
      term.textContent = label;
      const description = document.createElement("dd");
      description.textContent = value;
      grid.append(term, description);
    }
    details.append(grid);
  }
  story.append(details);
}

function appendResolution(resolution) {
  if (!resolution || resolution.mode === "automatic" && !resolution.consequences?.length) return;
  const zh = interfaceLanguage === "zh";
  const outcomeLabels = zh
    ? { impossible: "当前方法不可行", blocked: "受阻", limited_success: "有限成功", success: "成功", strong_success: "显著成功" }
    : { impossible: "Method impossible", blocked: "Blocked", limited_success: "Limited success", success: "Success", strong_success: "Strong success" };
  const attributeLabels = zh
    ? { physique: "体魄", agility: "身手", perception: "感知", intellect: "智识", will: "心性", charisma: "魅力", mystic_power: "灵能" }
    : { physique: "Physique", agility: "Agility", perception: "Perception", intellect: "Intellect", will: "Will", charisma: "Charisma", mystic_power: "Mystic power" };
  const details = document.createElement("details");
  details.className = "turn-resolution";
  const summary = document.createElement("summary");
  summary.textContent = zh ? "裁定依据" : "Resolution";
  const result = document.createElement("p");
  const parts = [outcomeLabels[resolution.outcome] ?? resolution.outcome];
  if (resolution.primary_attribute) parts.push(attributeLabels[resolution.primary_attribute] ?? resolution.primary_attribute);
  if (resolution.attribute_gap?.status === "known") {
    parts.push(zh ? `直接对抗差值 ${resolution.attribute_gap.difference}` : `Direct gap ${resolution.attribute_gap.difference}`);
  } else if (resolution.direct_contest && resolution.attribute_gap?.status === "unfixed") {
    parts.push(zh ? "属性尚未固定" : "Attributes not fixed");
  }
  result.textContent = parts.join(" · ");
  const reason = document.createElement("small");
  reason.textContent = resolution.reason;
  details.append(summary, result, reason);
  story.append(details);
}

function appendTokenUsage(usage) {
  const line = document.createElement("p");
  line.className = "turn-token-usage";
  const zh = interfaceLanguage === "zh";
  if (!usage?.available) {
    line.textContent = zh ? "Token：无法完整统计（旧回合或调用未提供用量）" : "Tokens: incomplete (older turn or usage not provided)";
  } else {
    const number = (value) => Number(value).toLocaleString();
    line.textContent = zh
      ? `本轮 Token：${number(usage.total)}（输入 ${number(usage.input)} · 输出 ${number(usage.output)}${usage.cached_input ? ` · 其中缓存输入 ${number(usage.cached_input)}` : ""}${usage.requests > 1 ? ` · ${usage.requests} 次调用` : ""}）`
      : `Turn tokens: ${number(usage.total)} (input ${number(usage.input)} · output ${number(usage.output)}${usage.cached_input ? ` · cached input ${number(usage.cached_input)}` : ""}${usage.requests > 1 ? ` · ${usage.requests} requests` : ""})`;
  }
  line.title = zh ? "由 Codex 返回的实际用量；输入包含缓存输入，输出包含推理 token。" : "Actual usage reported by Codex; input includes cached input and output includes reasoning tokens.";
  story.append(line);
}

function savedTokenUsage(turn) {
  try { return JSON.parse(turn.scene_json || "{}")._token_usage; } catch { return null; }
}

function savedActionFrame(turn) {
  try {
    return JSON.parse(turn.scene_json || "{}")._action_frame;
  } catch {
    return null;
  }
}

function savedResolution(turn) {
  try { return JSON.parse(turn.scene_json || "{}").resolution; } catch { return null; }
}

function resetStory(message) {
  story.replaceChildren();
  append("opening", message);
}

// Read-only play notes and maintenance tools share the same saved data, but
// never share the same visible surface.
journalRecords.append(
  document.querySelector("#character-drawer"), document.querySelector("#possessions-drawer"),
  document.querySelector("#cast-drawer")
);
document.querySelector("#possessions-drawer summary span").textContent = "Backpack & equipment";
document.querySelector("#cast-drawer summary span").textContent = "Party & people";
const journalDrawers = {
  character: [document.querySelector("#character-drawer")],
  backpack: [document.querySelector("#possessions-drawer")],
  party: [document.querySelector("#cast-drawer")]
};
function showJournalSection(section = "character") {
  activeJournalSection = journalDrawers[section] ? section : "character";
  for (const [key, drawers] of Object.entries(journalDrawers)) {
    for (const drawer of drawers) {
      drawer.hidden = key !== activeJournalSection;
      if (key === activeJournalSection) drawer.open = true;
    }
  }
  for (const tab of document.querySelectorAll("#journal-tabs [data-section]")) {
    const selected = tab.dataset.section === activeJournalSection;
    tab.dataset.active = String(selected);
    tab.setAttribute("aria-selected", String(selected));
  }
  gameJournal.scrollTop = 0;
}
for (const tab of document.querySelectorAll("#journal-tabs [data-section]")) {
  tab.addEventListener("click", () => showJournalSection(tab.dataset.section));
}
showJournalSection();

function openInformationCard(section = "character") {
  closeMap();
  gameJournal.hidden = false;
  openJournalButton.setAttribute("aria-expanded", "true");
  showJournalSection(section);
  closeJournalButton.focus();
}

function closeJournal() {
  gameJournal.hidden = true;
  openJournalButton.setAttribute("aria-expanded", "false");
}

function closeMap() {
  gameMap.hidden = true;
  openMapButton.setAttribute("aria-expanded", "false");
}

function renderMap(data) {
  loadedMap = data;
  mapCurrentName.textContent = data.current;
  mapMood.textContent = data.current_profile.mood;
  mapParent.textContent = data.current_place?.parent_name || (interfaceLanguage === "zh" ? "尚未明确" : "Not yet established");
  mapPlaceState.textContent = data.current_place?.current_summary || (
    data.current_place?.status && data.current_place.status !== "active" ? data.current_place.status :
      (interfaceLanguage === "zh" ? "没有已记录的长期变化" : "No lasting change recorded")
  );
  mapFocus.textContent = data.current_profile.focus;
  mapDanger.textContent = data.current_profile.danger;
  mapPlaces.replaceChildren();
  for (const place of data.places) {
    const row = document.createElement("li");
    if (place.name === data.current) row.className = "current";
    const name = document.createElement("strong");
    name.textContent = place.name;
    const detail = document.createElement("small");
    const parent = place.parent_name ? `${interfaceLanguage === "zh" ? "位于" : "within "}${place.parent_name} · ` : "";
    const reached = place.first_turn ? `${interfaceLanguage === "zh" ? "第" : "Turn "}${place.first_turn}${interfaceLanguage === "zh" ? "回合抵达" : " first reached"}` : (interfaceLanguage === "zh" ? "出发地" : "Starting place");
    const state = place.current_summary || (place.status && place.status !== "active" ? place.status : "");
    detail.textContent = `${parent}${state ? `${state} · ` : ""}${reached}`;
    row.append(name, detail);
    mapPlaces.append(row);
  }
  mapRoutes.replaceChildren();
  for (const route of data.routes) {
    const row = document.createElement("li");
    const state = route.status && route.status !== "open" ? ` · ${route.status}` : "";
    row.textContent = `${route.from} ↔ ${route.to}${state}${route.description ? ` · ${route.description}` : ""}`;
    mapRoutes.append(row);
  }
  if (!data.routes.length) {
    const empty = document.createElement("li");
    empty.textContent = interfaceLanguage === "zh" ? "还没有记录到地点间的移动。" : "No journey between places recorded yet.";
    mapRoutes.append(empty);
  }
  if (activeWorldSnapshot) {
    worldMeta.textContent = `${activeWorldSnapshot.player_name} · ${data.current}`;
    gameSceneLocation.textContent = data.current;
  }
}

async function loadMap() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/map");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read map.");
    renderMap(data);
  } catch (error) {
    mapCurrentName.textContent = error instanceof Error ? error.message : "Could not read map.";
  }
}

function toggleMap() {
  const opening = gameMap.hidden;
  closeJournal();
  gameMap.hidden = !opening;
  openMapButton.setAttribute("aria-expanded", String(opening));
  if (opening) {
    mapCurrentName.textContent = localized("Reading location…");
    void loadMap();
    closeMapButton.focus();
  }
}

function toggleJournal() {
  closeMap();
  gameJournal.hidden = !gameJournal.hidden;
  openJournalButton.setAttribute("aria-expanded", String(!gameJournal.hidden));
  if (!gameJournal.hidden) {
    showJournalSection(activeJournalSection);
    closeJournalButton.focus();
  }
}

function setView(view) {
  if (view !== "game") { closeJournal(); closeMap(); }
  shell.dataset.view = view;
  homeScreen.hidden = view !== "home";
  worldsScreen.hidden = view !== "worlds";
  universeScreen.hidden = view !== "universe";
  settingsScreen.hidden = view !== "settings";
  gameScreen.hidden = view !== "game";
  const buttons = [[navHomeButton, "home"], [navWorldsButton, "worlds"], [navUniverseButton, "universe"], [navSettingsButton, "settings"]];
  for (const [control, name] of buttons) control.classList.toggle("active", name === view);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showHome() { setView("home"); }

function showWorlds(create = false) {
  setView("worlds");
  createWorldPanel.hidden = !create;
  if (create) presetDetailPanel.hidden = true;
  if (create) {
    renderCharacterPresets();
    syncCreatorChoices();
    updateCharacterPreview();
    worldTitle.focus();
  }
}

function creatorFieldValue(control, customControl) {
  return control.value === "custom" ? customControl.value.trim() : control.value.trim();
}

function showCustomField(control, wrap) {
  wrap.hidden = control.value !== "custom";
}

const locationGuides = Object.freeze({
  "王冠城 · 旧渡口": { en: "Crown City is an old royal river capital. The Old Ferry is where toll collectors, boat crews, petitioners, and people avoiding the gates meet.", zh: "王冠城是古老的王室河都；旧渡口聚集着税吏、船员、请愿者，以及不愿走城门的人。" },
  "碧帆港 · 静塔旧区": { en: "Azure Sail Port is a free harbor whose quiet tower ward keeps records, maps, and bargains that merchants prefer forgotten.", zh: "碧帆港是自由港；静塔旧区保存着商人希望被忘掉的账本、海图与交易。" },
  "卡拉德门 · 封门庭": { en: "Karad Gate is a stone federation city, where guild work and a reopened deep-road dispute are both pressing matters.", zh: "卡拉德门属于石门联邦；工坊秩序与深岩重启争议同样迫在眉睫。" },
  "寒港 · 白鲸祠": { en: "Cold Harbor faces the northern waters. Its shrine, winter council, and arriving ships make rumor a local currency.", zh: "寒港面对北方海域；白鲸祠、冬议与归港船只让传闻成为当地的另一种货币。" },
  "月井城 · 第一渠": { en: "Moonwell City lives by carefully shared water. At the First Canal, every favor eventually becomes a question of rights.", zh: "月井城依靠谨慎分配的水而生；第一渠旁的每份人情，最终都会变成水权问题。" },
  "长河集 · 盟旗石": { en: "Longriver Fair is a meeting ground for travelling peoples. The banner stone remembers agreements more clearly than many officials do.", zh: "长河集是迁徙者的会面之地；盟旗石比许多官员更清楚地记得旧约。" },
  "鹿铃集 · 空田": { en: "Deerbell Fair sits where forest paths and new works meet. An empty field has become the center of a disagreement no one calls a conflict yet.", zh: "鹿铃集位于林径与新工程交会处；一片空田正成为无人愿称作冲突的争端中心。" },
  "风帆港 · 归帆碑": { en: "Windward Port honors ships that return, and does not easily forgive those that return without everyone aboard.", zh: "风帆港纪念归来的船，也不轻易原谅未能带回所有人的归航者。" },
  "双灯城 · 灰岸档案室": { en: "Twinlamp City survives on neutrality. The Greyshore archives can make a private history suddenly public.", zh: "双灯城靠中立立足；灰岸档案室能让一段私人历史突然变成公共问题。" }
});

function syncCreatorChoices() {
  showCustomField(worldLocation, worldLocationCustomWrap);
  showCustomField(worldOrigin, worldOriginCustomWrap);
  showCustomField(worldConcept, worldConceptCustomWrap);
  showCustomField(worldBond, worldBondCustomWrap);
  showCustomField(worldBurden, worldBurdenCustomWrap);
  const guide = locationGuides[creatorFieldValue(worldLocation, worldLocationCustom)];
  creatorChoiceNote.textContent = guide ? guide[interfaceLanguage] : (interfaceLanguage === "zh" ? "选择一个地点，即可看到当地局势和容易进入故事的方向。" : "Choose a place to see the local situation and an easy first-story direction.");
  updateCharacterPreview();
}

function presetDetailSection(title, className = "") {
  const section = document.createElement("section");
  section.className = `preset-detail-section${className ? ` ${className}` : ""}`;
  const heading = document.createElement("h3");
  heading.textContent = title;
  section.append(heading);
  return section;
}

function presetDetailText(label, value) {
  const row = document.createElement("div");
  row.className = "preset-detail-fact";
  const name = document.createElement("dt");
  name.textContent = label;
  const detail = document.createElement("dd");
  detail.textContent = value || (interfaceLanguage === "zh" ? "未记录" : "Not recorded");
  row.append(name, detail);
  return row;
}

function presetAbilityName(id) {
  const ability = startingAbilityCatalog.find((entry) => entry.id === id);
  if (ability?.name) return ability.name;
  return String(id || "").replace(/^technique_/, "").replace(/^trait_/, "").replaceAll("_", " ");
}

function presetMasteryLabel(mastery) {
  if (interfaceLanguage !== "zh") return mastery || "Recorded";
  return { mastered: "精通", skilled: "熟练", familiar: "熟悉", trained: "受训" }[mastery] || mastery || "已记录";
}

function presetStatusLabel(value) {
  if (interfaceLanguage !== "zh") return value || "Recorded";
  return { unhurt: "无伤", equipped: "已装备", carried: "随身携带", concealed: "隐蔽携带", stored: "已存放", party: "同行" }[value] || value || "已记录";
}

function renderPresetDetail(preset) {
  const defaults = preset.defaults ?? {};
  const setup = preset.setup ?? {};
  const character = setup.player_state ?? {};
  const mechanics = character.mechanics ?? {};
  const scene = setup.scene ?? {};
  const items = Array.isArray(setup.items) ? setup.items : [];
  const people = Array.isArray(setup.people) ? setup.people : [];
  presetDetailTitle.textContent = preset.title;
  presetDetailContent.replaceChildren();

  const background = presetDetailSection(interfaceLanguage === "zh" ? "故事背景" : "Story background", "preset-story-background");
  const backgroundText = document.createElement("p");
  backgroundText.textContent = preset.description || preset.summary || "";
  background.append(backgroundText);
  presetDetailContent.append(background);

  const facts = presetDetailSection(interfaceLanguage === "zh" ? "开局状态" : "Opening state", "preset-detail-facts");
  const factGrid = document.createElement("dl");
  factGrid.append(
    presetDetailText(interfaceLanguage === "zh" ? "人物" : "Character", defaults.player || preset.title),
    presetDetailText(interfaceLanguage === "zh" ? "身份" : "Calling", defaults.concept),
    presetDetailText(interfaceLanguage === "zh" ? "地点" : "Location", defaults.location),
    presetDetailText(interfaceLanguage === "zh" ? "状态" : "Condition", presetStatusLabel(character.condition)),
    presetDetailText(interfaceLanguage === "zh" ? "资金" : "Wallet", `${mechanics.resources?.wallet?.balance ?? 0} ${interfaceLanguage === "zh" ? "铜币" : "copper"}`)
  );
  facts.append(factGrid);
  presetDetailContent.append(facts);

  const attributes = presetDetailSection(interfaceLanguage === "zh" ? "初始属性" : "Starting attributes", "preset-attribute-section");
  const attributeGrid = document.createElement("div");
  attributeGrid.className = "preset-attribute-grid";
  const attributeLabels = interfaceLanguage === "zh"
    ? { physique: "体魄", agility: "敏捷", perception: "感知", intellect: "智识", will: "意志", charisma: "魅力", mystic_power: "灵能" }
    : { physique: "Physique", agility: "Agility", perception: "Perception", intellect: "Intellect", will: "Will", charisma: "Charisma", mystic_power: "Mystic power" };
  for (const key of attributeKeys) {
    const value = mechanics.attributes?.[key];
    const cell = document.createElement("div");
    const label = document.createElement("span");
    label.textContent = attributeLabels[key];
    const output = document.createElement("strong");
    output.textContent = value == null ? "—" : String(value);
    cell.append(label, output);
    attributeGrid.append(cell);
  }
  attributes.append(attributeGrid);
  presetDetailContent.append(attributes);

  const abilities = presetDetailSection(interfaceLanguage === "zh" ? "能力与专业" : "Abilities and specialties", "preset-ability-section");
  const abilityList = document.createElement("ul");
  abilityList.className = "preset-detail-list";
  for (const ability of mechanics.abilities ?? []) {
    const row = document.createElement("li");
    row.textContent = `${presetAbilityName(ability.id)} · ${presetMasteryLabel(ability.mastery)}`;
    abilityList.append(row);
  }
  for (const specialty of mechanics.specialties ?? []) {
    const row = document.createElement("li");
    row.textContent = `${interfaceLanguage === "zh" ? "专业" : "Specialty"} · ${specialty.name || specialty}`;
    abilityList.append(row);
  }
  abilities.append(abilityList);
  presetDetailContent.append(abilities);

  const sceneSection = presetDetailSection(interfaceLanguage === "zh" ? "第一幕" : "First scene", "preset-scene-section");
  const sceneText = document.createElement("p");
  sceneText.textContent = scene.immediate_situation || defaults.character?.opening_pressure || "";
  sceneSection.append(sceneText);
  const sceneMeta = document.createElement("small");
  sceneMeta.textContent = [scene.location, scene.state?.activity, scene.state?.threat].filter(Boolean).join(" · ");
  sceneSection.append(sceneMeta);
  presetDetailContent.append(sceneSection);

  const partySection = presetDetailSection(interfaceLanguage === "zh" ? "同行者" : "Party", "preset-party-section");
  const partyList = document.createElement("div");
  partyList.className = "preset-party-list";
  for (const person of people) {
    const card = document.createElement("article");
    card.className = "preset-party-card";
    const name = document.createElement("h4");
    name.textContent = person.name;
    const role = document.createElement("p");
    role.textContent = person.profile?.role || "";
    const relationship = document.createElement("p");
    relationship.textContent = person.state?.relationship || "";
    const state = document.createElement("small");
    state.textContent = [person.state?.location, person.state?.activity, person.state?.availability].filter(Boolean).join(" · ");
    const partyAbilities = (person.state?.mechanics?.abilities ?? []).map((ability) => `${presetAbilityName(ability.id)} · ${presetMasteryLabel(ability.mastery)}`);
    const partySpecialties = (person.state?.mechanics?.specialties ?? []).map((value) => value.name || value);
    const skills = document.createElement("small");
    skills.textContent = [...partyAbilities, ...partySpecialties].join(" · ");
    card.append(name, role, relationship, state, skills);
    partyList.append(card);
  }
  partySection.append(partyList);
  presetDetailContent.append(partySection);

  const equipmentSection = presetDetailSection(interfaceLanguage === "zh" ? "初始装备" : "Starting equipment", "preset-equipment-section");
  const equipmentList = document.createElement("ul");
  equipmentList.className = "preset-detail-list preset-equipment-list";
  for (const item of items) {
    const row = document.createElement("li");
    const holder = item.state?.holder === "player" ? (defaults.player || preset.title) : people.find((person) => person.id === item.state?.holder)?.name || item.state?.holder;
    row.textContent = `${item.name}${item.state?.quantity > 1 ? ` ×${item.state.quantity}` : ""} · ${holder} · ${presetStatusLabel(item.state?.status)}${item.state?.equipped_as ? ` · ${item.state.equipped_as}` : ""}`;
    equipmentList.append(row);
  }
  equipmentSection.append(equipmentList);
  presetDetailContent.append(equipmentSection);
}

function showPresetDetail(preset) {
  selectedCharacterPresetId = preset.id;
  createWorldPanel.hidden = true;
  presetDetailPanel.hidden = false;
  renderPresetDetail(preset);
  renderCharacterPresets();
  presetDetailPanel.scrollIntoView({ behavior: "smooth", block: "start" });
  startPresetStoryButton.focus();
}

function closePresetDetail() {
  selectedCharacterPresetId = "";
  presetDetailPanel.hidden = true;
  renderCharacterPresets();
}

async function startPresetStory() {
  const preset = characterPresets.find((entry) => entry.id === selectedCharacterPresetId);
  if (!preset) return;
  startPresetStoryButton.disabled = true;
  try {
    const defaults = preset.defaults ?? {};
    const response = await saveRequest("/api/worlds", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ preset_id: preset.id, title: defaults.title ?? preset.title, player: defaults.player ?? preset.title })
    });
    selectedCharacterPresetId = "";
    presetDetailPanel.hidden = true;
    renderWorlds(response);
    const world = response.worlds.find((entry) => entry.id === response.active_campaign);
    showGame(world);
    void loadSaveState();
    void loadPossessions();
    void loadCast();
    void loadLore();
    void loadUniverseLore();
    void loadTimeline();
  } catch (error) {
    worldStatus.textContent = error instanceof Error ? error.message : (interfaceLanguage === "zh" ? "无法开始这个预设故事。" : "Could not start this preset story.");
  } finally {
    startPresetStoryButton.disabled = false;
  }
}

function renderCharacterPresets() {
  characterPresetList.replaceChildren();
  if (!characterPresets.length) {
    const empty = document.createElement("p");
    empty.className = "save-help";
    empty.textContent = localized("No preset stories are installed.");
    characterPresetList.append(empty);
    return;
  }
  for (const preset of characterPresets) {
    const card = document.createElement("article");
    card.className = "character-preset";
    const title = document.createElement("strong");
    title.textContent = preset.title;
    const detail = document.createElement("span");
    detail.textContent = preset.summary;
    const backgroundLabel = document.createElement("span");
    backgroundLabel.className = "preset-background-label";
    backgroundLabel.textContent = interfaceLanguage === "zh" ? "故事背景" : "Story background";
    const description = document.createElement("span");
    description.className = "preset-description";
    description.textContent = preset.description;
    const action = document.createElement("button");
    action.type = "button";
    action.textContent = localized("View save");
    card.classList.toggle("selected", selectedCharacterPresetId === preset.id);
    card.append(title, detail, backgroundLabel, description, action);
    action.addEventListener("click", () => showPresetDetail(preset));
    characterPresetList.append(card);
  }
}

function setCreatorValue(control, customControl, value) {
  const normalized = String(value ?? "").trim();
  const option = [...control.options].find((entry) => entry.value === normalized);
  if (option) {
    control.value = normalized;
    if (customControl) customControl.value = "";
  } else if (normalized && customControl) {
    control.value = "custom";
    customControl.value = normalized;
  } else {
    control.value = "";
  }
}

async function loadCharacterPresets() {
  const response = await fetch("/api/character-presets");
  const data = await response.json();
  if (!response.ok) throw new Error(data.error ?? "Could not load starting characters.");
  characterPresets = Array.isArray(data.presets) ? data.presets : [];
  startingAbilityCatalog = Array.isArray(data.ability_catalog) ? data.ability_catalog : [];
  renderCharacterPresets();
}

function characterDraft() {
  const ancestry = worldAncestry.value === "other" ? worldLineage.value.trim() : worldAncestry.value;
  return {
    pronouns: worldPronouns.value.trim(),
    ancestry,
    lineage: worldLineage.value.trim(),
    appearance: worldAppearance.value.trim(),
    origin: creatorFieldValue(worldOrigin, worldOriginCustom),
    bond: creatorFieldValue(worldBond, worldBondCustom),
    burden: creatorFieldValue(worldBurden, worldBurdenCustom),
    temperament: worldTemperament.value.trim(),
    opening_pressure: worldBackground.value.trim()
  };
}

function updateCharacterPreview() {
  const name = worldPlayer.value.trim() || (interfaceLanguage === "zh" ? "这个人" : "This person");
  const ancestry = worldAncestry.value === "other" ? worldLineage.value.trim() : worldAncestry.value;
  const calling = creatorFieldValue(worldConcept, worldConceptCustom);
  const origin = creatorFieldValue(worldOrigin, worldOriginCustom);
  const pieces = [ancestry, calling, origin].filter(Boolean).map(localized);
  characterPreviewCopy.textContent = pieces.length
    ? (interfaceLanguage === "zh" ? `${name}将以 ${pieces.join(" · ")} 的身份进入故事。` : `${name} enters the story as ${pieces.join(" · ")}.`)
    : (interfaceLanguage === "zh" ? "一段人生，正等待第一个决定性的时刻。" : "A life waiting for its first decisive moment.");
}

for (const control of [worldPlayer, worldAncestry, worldLineage, worldConcept, worldConceptCustom, worldOrigin, worldOriginCustom, worldLocation, worldLocationCustom, worldBond, worldBondCustom, worldBurden, worldBurdenCustom, worldBackground]) {
  control.addEventListener("input", updateCharacterPreview);
  control.addEventListener("change", updateCharacterPreview);
}
for (const control of [worldLocation, worldOrigin, worldConcept, worldBond, worldBurden, worldLocationCustom, worldOriginCustom, worldConceptCustom, worldBondCustom, worldBurdenCustom]) {
  control.addEventListener("input", syncCreatorChoices);
  control.addEventListener("change", syncCreatorChoices);
}
worldOpeningPreset.addEventListener("change", () => {
  if (worldOpeningPreset.value) worldBackground.value = worldOpeningPreset.value;
  updateCharacterPreview();
});
closePresetDetailButton.addEventListener("click", closePresetDetail);
startPresetStoryButton.addEventListener("click", () => void startPresetStory());

function showUniverse() {
  setView("universe");
  void loadUniverseLore();
}

function showSettings() { setView("settings"); void loadModels(); }

function showManagement() {
  if (!activeWorldId) return;
  setView("manage");
  void loadSaveState();
  void loadPossessions();
  void loadCast();
  void loadLore();
  void loadChapters();
}

const attributeKeys = Object.freeze([
  "physique", "agility", "perception", "intellect", "will", "charisma", "mystic_power"
]);

function attributeValue(world, key) {
  const sources = [
    world?.player_state?.mechanics?.attributes,
    world?.player_state?.attributes,
    world?.character?.attributes
  ];
  for (const source of sources) {
    const raw = source?.[key];
    if (typeof raw === "number" && Number.isFinite(raw)) return raw;
    if (typeof raw?.value === "number" && Number.isFinite(raw.value)) return raw.value;
  }
  return null;
}

function characterIdentity(world) {
  const character = world?.character ?? {};
  const pieces = [character.ancestry, character.lineage, character.origin, world?.player_concept]
    .map((value) => String(value ?? "").trim())
    .filter((value, index, all) => value && all.indexOf(value) === index && value !== "adventurer")
    .map((value) => localized(value));
  return pieces.join(" · ") || localized("No declared identity");
}

function characterDescription(world) {
  const character = world?.character ?? {};
  return character.appearance || character.temperament || character.bond
    || (interfaceLanguage === "zh" ? "这个人的更多细节会在故事中逐渐形成。" : "More of this person will take shape through play.");
}

function renderCharacterProfile(character = {}) {
  const labels = interfaceLanguage === "zh"
    ? { ancestry: "血统", lineage: "传承", origin: "出身", appearance: "外貌", temperament: "性格", bond: "重要关系", burden: "背负之事", opening_pressure: "当前牵引" }
    : { ancestry: "Ancestry", lineage: "Heritage", origin: "Origin", appearance: "Appearance", temperament: "Temperament", bond: "Important bond", burden: "Burden", opening_pressure: "Current pull" };
  const keys = ["ancestry", "lineage", "origin", "appearance", "temperament", "bond", "burden", "opening_pressure"];
  characterProfileGrid.replaceChildren();
  let count = 0;
  for (const key of keys) {
    const value = String(character[key] ?? "").trim();
    if (!value) continue;
    count += 1;
    const item = document.createElement("article");
    item.className = `character-profile-item character-profile-${key}`;
    const label = document.createElement("h4");
    label.textContent = labels[key];
    const detail = document.createElement("p");
    detail.textContent = localized(value);
    item.append(label, detail);
    characterProfileGrid.append(item);
  }
  characterProfileGrid.hidden = !count;
}

function conditionLabel(condition) {
  if (!condition || condition === "unhurt") return localized("Normal");
  return String(condition);
}

function sceneActivityLabel(activity) {
  const labels = interfaceLanguage === "zh"
    ? { everyday: "日常", dialogue: "交谈", exploration: "探索", travel: "行旅", trade: "交易", rest: "休整" }
    : { everyday: "Everyday", dialogue: "Dialogue", exploration: "Exploration", travel: "Travel", trade: "Trade", rest: "Rest" };
  return labels[activity] ?? labels.everyday;
}

function sceneThreatLabel(threat) {
  const labels = interfaceLanguage === "zh"
    ? { calm: "平稳", tense: "紧张", imminent: "迫近", combat: "战斗", aftermath: "战后" }
    : { calm: "Calm", tense: "Tense", imminent: "Imminent", combat: "Combat", aftermath: "Aftermath" };
  return labels[threat] ?? labels.calm;
}

function insertSceneReference(name) {
  const start = field.selectionStart ?? field.value.length;
  const end = field.selectionEnd ?? start;
  const before = field.value.slice(0, start);
  const after = field.value.slice(end);
  const prefix = before && !/\s$/.test(before) ? " " : "";
  const suffix = after && !/^\s/.test(after) ? " " : "";
  field.value = `${before}${prefix}${name}${suffix}${after}`;
  const cursor = before.length + prefix.length + name.length + suffix.length;
  field.setSelectionRange(cursor, cursor);
  closeJournal();
  field.focus();
}

function sceneAnchor(item, detail) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "scene-anchor";
  button.title = interfaceLanguage === "zh" ? `在行为中引用“${item.name}”` : `Reference ${item.name} in the action`;
  const name = document.createElement("strong");
  name.textContent = item.name;
  const description = document.createElement("small");
  description.textContent = detail;
  button.append(name, description);
  button.addEventListener("click", () => insertSceneReference(item.name));
  return button;
}

function renderPlayableScene() {
  // Keep the structured scene model for the narrator and old saves, while the
  // player-facing journey stays limited to scene, state, and prose.
  scenePlayableContext.hidden = true;
  scenePlayerPosition.hidden = true;
  sceneParticipantsSection.hidden = true;
  sceneElementsSection.hidden = true;
  scenePressuresSection.hidden = true;
  sceneParticipants.replaceChildren();
  sceneElements.replaceChildren();
  scenePressures.replaceChildren();
}

function renderGameOverview(world) {
  if (!world) return;
  const character = world.character ?? {};
  const playerState = world.player_state ?? {};
  const playerName = displayValue(world.player_name, "Unnamed character");
  const location = displayValue(world?.current_scene?.location || playerState.location || world.starting_location, "Unknown location");
  const turnCount = Number(world.turn_count ?? lastTimelineTurns.length ?? 0);
  const opening = String(character.opening_pressure || "").trim();
  const sceneState = world.scene_state ?? { activity: "everyday", threat: "calm", basis: "" };
  const activity = sceneActivityLabel(sceneState.activity);
  const threat = sceneThreatLabel(sceneState.threat);
  const situation = String(world?.current_scene?.immediate_situation || "").trim();
  const values = attributeKeys.map((key) => attributeValue(world, key));
  const assignedCount = values.filter((value) => value !== null).length;

  gamePlayerName.textContent = playerName;
  gamePlayerMark.textContent = playerName.trim().slice(0, 1).toUpperCase() || "?";
  gamePlayerDescription.textContent = characterDescription(world);
  renderCharacterProfile(character);
  gamePlayerLocation.textContent = location;
  gamePlayerCondition.textContent = conditionLabel(playerState.condition);
  gamePlayerIdentity.textContent = characterIdentity(world);
  characterSheetStatus.textContent = localized(assignedCount || Object.values(character).some(Boolean) ? "Profile ready" : "Profile open");
  attributeRecordStatus.textContent = localized(assignedCount ? "Assigned" : "Not assigned");
  attributeHeading.hidden = !assignedCount;
  gameAttributeGrid.hidden = !assignedCount;
  attributeSheetNote.hidden = Boolean(assignedCount);
  for (const [index, key] of attributeKeys.entries()) {
    const value = values[index];
    const output = gameAttributeGrid.querySelector(`[data-attribute="${key}"] strong`);
    if (output) output.textContent = value === null ? "—" : String(value);
  }

  const turnText = interfaceLanguage === "zh" ? `第 ${turnCount} 回合` : `Turn ${turnCount}`;
  gameTurnBadge.textContent = turnCount ? `${turnText} · ${threat}` : localized("Opening");
  gameTurnBadge.dataset.threat = sceneState.threat ?? "calm";
  scenePhaseLabel.textContent = turnCount ? `${activity} · ${threat}` : localized("Opening");
  gameSceneLocation.textContent = location;
  gameSceneObjective.textContent = situation || opening || localized("First scene has no fixed objective yet.");
  gameSceneTurn.textContent = turnText;
  gameScenePressure.textContent = sceneState.basis || (sceneState.threat === "calm" ? localized("No active pressure") : threat);
  journeyLocation.textContent = location;
  journeySituation.textContent = situation || opening || localized("The first situation has not been established.");
  journeyActivity.textContent = activity;
  journeyThreat.textContent = threat;
  journeyThreat.dataset.threat = sceneState.threat ?? "calm";
  renderPlayableScene(world.scene_model);
}

function renderAbilities(data) {
  const abilities = Array.isArray(data?.abilities) ? data.abilities : [];
  const maintained = new Set(Array.isArray(data?.maintained) ? data.maintained : []);
  abilityRecordStatus.textContent = abilities.length
    ? (interfaceLanguage === "zh" ? `${abilities.length} 项已掌握` : `${abilities.length} recorded`)
    : (interfaceLanguage === "zh" ? "尚无记录" : "None recorded");
  abilityList.replaceChildren();
  if (!abilities.length) {
    const empty = document.createElement("p");
    empty.className = "save-help";
    empty.textContent = interfaceLanguage === "zh"
      ? "尚未掌握已记录的特殊能力；普通行动仍可依靠属性、专业与现实条件进行。"
      : "No special abilities are recorded yet. Ordinary actions still use attributes, training, and real conditions.";
    abilityList.append(empty);
  } else {
    for (const ability of abilities) {
      const card = document.createElement("article");
      card.className = "ability-card";
      const heading = document.createElement("div");
      heading.className = "ability-card-heading";
      const title = document.createElement("h4");
      title.textContent = ability.name;
      const badge = document.createElement("span");
      badge.textContent = `${ability.mastery_label}${maintained.has(ability.id) ? (interfaceLanguage === "zh" ? " · 维持中" : " · Maintained") : ""}`;
      heading.append(title, badge);
      const effect = document.createElement("p");
      effect.textContent = ability.known_effect;
      const limits = document.createElement("small");
      limits.textContent = `${interfaceLanguage === "zh" ? "边界" : "Limits"}：${ability.limits}`;
      card.append(heading, effect, limits);
      abilityList.append(card);
    }
  }
  const loadLabels = interfaceLanguage === "zh"
    ? { physical: "身体", focus: "专注", mystic: "灵能" }
    : { physical: "Physical", focus: "Focus", mystic: "Mystic" };
  const loads = data?.loads ?? {};
  abilityLoads.replaceChildren(...Object.entries(loadLabels).map(([key, label]) => {
    const item = document.createElement("span");
    item.textContent = `${label} · ${loads[key] ?? (interfaceLanguage === "zh" ? "稳定" : "Stable")}`;
    return item;
  }));
  abilityLoads.hidden = false;
  const injuries = Array.isArray(data?.injuries) ? data.injuries : [];
  const conditions = Array.isArray(data?.conditions) ? data.conditions : [];
  consequenceList.replaceChildren();
  for (const injury of injuries) {
    const item = document.createElement("article");
    item.className = "condition-record";
    const stage = interfaceLanguage === "zh"
      ? { minor: "轻伤", serious: "重伤", critical: "危重" }[injury.stage]
      : { minor: "Minor", serious: "Serious", critical: "Critical" }[injury.stage];
    const title = document.createElement("strong");
    title.textContent = `${injury.label} · ${stage ?? injury.stage}`;
    const effect = document.createElement("span");
    effect.textContent = injury.affected_functions?.join("、") || injury.source;
    const recovery = document.createElement("small");
    recovery.textContent = `${interfaceLanguage === "zh" ? "恢复" : "Recovery"}：${injury.recovery_condition}`;
    item.append(title, effect, recovery);
    consequenceList.append(item);
  }
  for (const condition of conditions) {
    const item = document.createElement("article");
    item.className = "condition-record";
    const title = document.createElement("strong");
    title.textContent = condition.label;
    const effect = document.createElement("span");
    effect.textContent = condition.effect;
    const recovery = document.createElement("small");
    recovery.textContent = `${interfaceLanguage === "zh" ? "解除" : "Clear"}：${condition.recovery_condition}`;
    item.append(title, effect, recovery);
    consequenceList.append(item);
  }
  consequenceList.hidden = !injuries.length && !conditions.length;
}

async function loadAbilities() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/abilities");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read abilities.");
    loadedAbilities = data;
    renderAbilities(data);
  } catch (error) {
    abilityList.replaceChildren();
    const failed = document.createElement("p");
    failed.className = "save-help";
    failed.textContent = error instanceof Error ? error.message : "Could not read abilities.";
    abilityList.append(failed);
  }
}

function renderEmptyStory(world) {
  story.replaceChildren();
  const character = world?.character ?? {};
  const location = world?.player_state?.location || world?.starting_location || localized("Not set");
  const opening = String(character.opening_narration || character.opening_pressure || "").trim();
  const panel = document.createElement("article");
  panel.className = "story-opening";
  const kicker = document.createElement("p");
  kicker.className = "card-kicker";
  kicker.textContent = localized("FIRST SCENE");
  const title = document.createElement("h2");
  title.textContent = location;
  const place = document.createElement("p");
  place.className = "story-opening-lead";
  place.textContent = opening || localized("A story begins here.");
  const introduction = document.createElement("p");
  introduction.textContent = localized("The room is waiting for your answer.");
  const hint = document.createElement("small");
  hint.textContent = localized("Write what you do, say, or notice below. There are no fixed choices.");
  panel.append(kicker, title, place, introduction, hint);
  story.append(panel);
}

function showGame(world) {
  if (!world) {
    showWorlds();
    return;
  }
  const changedWorld = activeWorldSnapshot?.id !== world.id;
  activeWorldSnapshot = world;
  setView("game");
  worldName.textContent = world.title;
  worldUniverseLabel.textContent = localized(displayValue(world.universe_title, "The Lost Lands"));
  worldMeta.textContent = `${displayValue(world.player_name, "Unnamed character")} · ${displayValue(world.player_state?.location || world.starting_location, "Unknown location")}`;
  renderGameOverview(world);
  if (changedWorld) {
    story.replaceChildren();
    lastTimelineTurns = [];
    if (!world.turn_count) renderEmptyStory(world);
  }
  renderCastChanges([]);
  window.scrollTo({ top: 0, behavior: "smooth" });
  void loadTimeline();
  void loadPossessions();
  void loadAbilities();
  void loadCast();
  void loadChapters();
}

function renderTimeline(turns) {
  lastTimelineTurns = turns;
  story.replaceChildren();
  if (!turns.length) {
    if (activeWorldSnapshot) {
      activeWorldSnapshot = { ...activeWorldSnapshot, turn_count: 0 };
      renderGameOverview(activeWorldSnapshot);
    }
    renderEmptyStory(activeWorldSnapshot);
    return;
  }
  for (const turn of turns) {
    append("action", turn.player_action, false);
    append("narration", turn.narration, false);
  }
  if (activeWorldSnapshot) {
    activeWorldSnapshot = { ...activeWorldSnapshot, turn_count: turns.at(-1)?.turn_number ?? turns.length };
    renderGameOverview(activeWorldSnapshot);
  }
  requestAnimationFrame(() => {
    storyScroll.scrollTop = storyScroll.scrollHeight;
  });
}

async function refreshActiveWorldOverview() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/worlds");
    const data = await response.json();
    if (!response.ok) return;
    const world = data.worlds?.find((item) => item.id === activeWorldId);
    if (!world) return;
    activeWorldSnapshot = world;
    renderGameOverview(world);
  } catch {
    // The completed turn remains visible even if this optional overview refresh fails.
  }
}

async function loadTimeline() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/timeline");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read this chronicle.");
    renderTimeline(data.turns);
  } catch (error) {
    resetStory(error instanceof Error ? error.message : "Could not read this chronicle.");
  }
}

function renderWorlds(state) {
  const active = state.active_campaign;
  if (activeWorldId !== active) loadedMap = null;
  activeWorldId = active;
  journalStatus.textContent = "";
  const activeWorld = state.worlds.find((world) => world.id === active);
  const playable = Boolean(activeWorld);
  field.disabled = !playable;
  speechField.disabled = !playable;
  button.disabled = !playable;
  modelSelect.disabled = modelSelect.dataset.loaded !== "true" || modelSelect.dataset.pinned === "true";
  if (activeWorld) {
    status.textContent = localized(modelSelect.dataset.pinned === "true" ? "Narrator model is fixed for this local session." : "Ready when you are.");
    homeCurrentTitle.textContent = activeWorld.title;
    homeCurrentMeta.textContent = `${displayValue(activeWorld.player_name, "Unnamed character")} · ${localized(displayValue(activeWorld.player_concept, "Unspecified calling"))} · ${displayValue(activeWorld.starting_location, "Unknown location")}`;
    continueWorldButton.disabled = false;
    continueWorldButton.onclick = () => {
      showGame(activeWorld);
      void loadSaveState();
      void loadPossessions();
      void loadCast();
      void loadLore();
      void loadTimeline();
    };
  } else {
    homeCurrentTitle.textContent = "No chronicle selected";
    homeCurrentMeta.textContent = "Create a world when you are ready to begin.";
    continueWorldButton.disabled = true;
  }
  worldStatus.textContent = active
    ? (interfaceLanguage === "zh" ? `本机共有 ${state.worlds.length} 个故事。` : `${state.worlds.length} chronicle${state.worlds.length === 1 ? "" : "s"} in your local archive.`)
    : localized("Create your first chronicle, or return to one below.");
  renderUniverseOptions(state.universes, activeWorld?.universe_id);
  void loadUniverseLore();
  worldList.replaceChildren();
  worldListSidebar.replaceChildren();
  worldTrashList.replaceChildren();
  const removed = state.trashed_worlds ?? [];
  worldTrash.hidden = !removed.length;
  worldTrashCount.textContent = `(${removed.length})`;
  for (const world of removed) {
    const row = document.createElement("li");
    const label = document.createElement("strong");
    label.textContent = world.title;
    const detail = document.createElement("small");
    detail.textContent = `${world.player_name} · ${world.starting_location}`;
    row.append(label, detail);
    const restore = actionButton(localized("Restore"), async (control) => {
      control.disabled = true;
      try {
        renderWorlds(await saveRequest(`/api/worlds/${encodeURIComponent(world.id)}/restore`, { method: "POST" }));
      } catch (error) {
        worldStatus.textContent = error instanceof Error ? error.message : "Could not restore this story.";
        control.disabled = false;
      }
    });
    restore.disabled = Boolean(state.pinned);
    const purge = actionButton(localized("Permanently delete"), async (control) => {
      const warning = interfaceLanguage === "zh"
        ? `确认永久删除“${world.title}”（${world.player_name}）？此世界的全部剧情、时间线、存档点、人物和物品将从当前本地数据库清除，无法从“最近删除”恢复。已有的独立备份不会自动删除。`
        : `Permanently delete “${world.title}” (${world.player_name})? All its turns, timelines, saves, people, and items will be removed from the current local database and cannot be restored from Recently removed. Separate backups are not deleted.`;
      if (!confirm(warning)) return;
      control.disabled = true;
      restore.disabled = true;
      try {
        renderWorlds(await saveRequest(`/api/worlds/${encodeURIComponent(world.id)}/purge`, {
          method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ confirm: world.id })
        }));
      } catch (error) {
        worldStatus.textContent = error instanceof Error ? error.message : "Could not permanently delete this story.";
        control.disabled = false;
        restore.disabled = false;
      }
    }, true);
    purge.disabled = Boolean(state.pinned);
    const actions = document.createElement("div");
    actions.className = "world-card-actions";
    actions.append(restore, purge);
    row.append(actions);
    worldTrashList.append(row);
  }
  if (!state.worlds.length) {
    const empty = document.createElement("li");
    empty.textContent = interfaceLanguage === "zh" ? "还没有玩家存档。可以从上方预设开始，或创建自定义开局。" : "No player saves yet. Start from a preset above or create a custom story.";
    worldList.append(empty);
    const sidebarEmpty = document.createElement("li");
    sidebarEmpty.className = "empty-worlds";
    sidebarEmpty.textContent = "Your stories will appear here.";
    worldListSidebar.append(sidebarEmpty);
    return;
  }
  for (const world of state.worlds) {
    const row = document.createElement("li");
    const label = document.createElement("strong");
    const isActive = world.id === active;
    row.className = `world-card${isActive ? " active" : ""}`;
    label.textContent = world.title;
    if (isActive) label.className = "active";
    const details = document.createElement("small");
    details.textContent = `${localized(world.universe_title)} · ${displayValue(world.player_name, "Unnamed character")} — ${localized(displayValue(world.player_concept, "Unspecified calling"))} · ${displayValue(world.starting_location, "Unknown location")}`;
    row.append(label, details);
    const actions = document.createElement("div");
    actions.className = "world-card-actions";
    actions.append(actionButton(localized(isActive ? "Continue" : "Enter world"), () => isActive ? showGame(world) : selectWorld(world)));
    const remove = actionButton(localized("Delete story"), async (control) => {
      const warning = interfaceLanguage === "zh"
        ? `将“${world.title}”（${world.player_name}）移入回收区？所有剧情、存档点、小队与物品都会保留，可在此页恢复。`
        : `Move “${world.title}” (${world.player_name}) to recently removed? All turns, saves, party, and items remain recoverable here.`;
      if (!confirm(warning)) return;
      control.disabled = true;
      try {
        renderWorlds(await saveRequest(`/api/worlds/${encodeURIComponent(world.id)}/trash`, { method: "POST" }));
      } catch (error) {
        worldStatus.textContent = error instanceof Error ? error.message : "Could not remove this story.";
        control.disabled = false;
      }
    }, true);
    remove.disabled = Boolean(state.pinned);
    actions.append(remove);
    row.append(actions);
    worldList.append(row);

    const sidebarRow = document.createElement("li");
    const sidebarButton = document.createElement("button");
    sidebarButton.type = "button";
    sidebarButton.className = `world-nav-item${isActive ? " active" : ""}`;
    const sidebarTitle = document.createElement("strong");
    sidebarTitle.textContent = world.title;
    const sidebarDetails = document.createElement("small");
    sidebarDetails.textContent = `${displayValue(world.player_name, "Unnamed character")} · ${displayValue(world.starting_location, "Unknown location")}`;
    sidebarButton.append(sidebarTitle, sidebarDetails);
    sidebarButton.addEventListener("click", () => {
      if (isActive) {
        showGame(world);
        return;
      }
      if (!state.pinned) void selectWorld(world);
    });
    sidebarRow.append(sidebarButton);
    worldListSidebar.append(sidebarRow);
  }
}

function renderUniverseOptions(universes, activeUniverseId) {
  // Kept as a seam for the save-state renderer. The interface intentionally
  // exposes one canon world rather than a universe picker.
  return universes.find((universe) => universe.id === selectedUniverseId) ?? null;
}

async function selectWorld(world) {
  try {
    const response = await saveRequest(`/api/worlds/${encodeURIComponent(world.id)}/select`, { method: "POST" });
    renderWorlds(response);
    showGame(response.worlds.find((item) => item.id === response.active_campaign));
    void loadSaveState();
    void loadPossessions();
    void loadCast();
    void loadLore();
    void loadUniverseLore();
    void loadTimeline();
  } catch (error) {
    worldStatus.textContent = error instanceof Error ? error.message : "Could not open this chronicle.";
  }
}

async function loadWorlds() {
  try {
    const response = await fetch("/api/worlds");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read local worlds.");
    renderWorlds(data);
  } catch (error) {
    worldStatus.textContent = error instanceof Error ? error.message : "Could not read local worlds.";
  }
}

function loreSearchText(entry) {
  const record = entry.record && typeof entry.record === "object" ? entry.record : {};
  const fieldText = Object.values(record.fields && typeof record.fields === "object" ? record.fields : {})
    .flatMap((value) => Array.isArray(value) ? value : [value]);
  const relationText = (record.relations ?? []).flatMap((relation) => [relation.type, relation.target]);
  return [entry.title, entry.content, entry.category, entry.reference, record.record_type, record.canonical_name,
    record.summary, record.status, record.region, ...(record.aliases ?? []), ...(record.tags ?? []),
    ...fieldText, ...relationText, ...(entry.keys ?? []), ...(entry.secondary_keys ?? [])]
    .join(" ").toLocaleLowerCase();
}

function loreSearchScore(entry, query) {
  const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (!terms.length) return 0;
  const haystack = loreSearchText(entry);
  if (!terms.every((term) => haystack.includes(term))) return -1;
  const title = String(entry.title ?? "").toLocaleLowerCase();
  const keys = [...(entry.keys ?? []), ...(entry.secondary_keys ?? [])].map((term) => String(term).toLocaleLowerCase());
  return terms.reduce((score, term) => score
    + (title === term ? 12 : title.includes(term) ? 7 : 0)
    + (keys.some((key) => key === term) ? 4 : 0), 0);
}

function encyclopediaGroupForSection(section) {
  return encyclopediaGroups.find((group) => group.sections.some((item) => item.id === section))?.id ?? "world";
}

function encyclopediaGroup(groupId) {
  return encyclopediaGroups.find((group) => group.id === groupId) ?? encyclopediaGroups[0];
}

function encyclopediaSection(sectionId) {
  return encyclopediaGroups.flatMap((group) => group.sections)
    .find((section) => section.id === sectionId) ?? { id: sectionId, source: "lore" };
}

const encyclopediaItemSubgroups = Object.freeze({
  Weapons: Object.freeze([
    { id: "weapon-blades", zh: "刀剑与短兵", en: "Blades & sidearms", types: ["weapon.sword", "weapon.sabre", "weapon.greatsword", "weapon.dagger", "weapon.knife", "weapon.rapier", "weapon.duelist", "weapon.kukri", "weapon.back_sword"] },
    { id: "weapon-hafted", zh: "斧锤与长柄兵器", en: "Axes, hammers & polearms", types: ["weapon.axe", "weapon.hook_axe", "weapon.spear", "weapon.shortspear", "weapon.lance", "weapon.polearm", "weapon.hook_blade", "weapon.long_axe", "weapon.blunt", "weapon.bludgeon", "weapon.staff", "weapon.quarterstaff", "weapon.warhammer", "weapon.armor_hammer", "weapon.warpick", "weapon.armor_pick", "weapon.halberd", "weapon.composite_polearm", "weapon.boar_spear", "weapon.beast_lance", "weapon.ice_pick", "weapon.climbing_chisel"] },
    { id: "weapon-ranged", zh: "弓弩、投掷与远射", en: "Bows, crossbows & thrown", types: ["weapon.bow", "weapon.hunting_bow", "weapon.longbow", "weapon.war_bow", "weapon.crossbow", "weapon.launcher", "weapon.repeating_crossbow", "weapon.magazine_crossbow", "weapon.tower_bow", "weapon.fixed_bow", "weapon.ammunition", "weapon.thrown", "weapon.sling", "weapon.catapult", "weapon.harpoon", "weapon.javelin", "weapon.thrown_spear", "weapon.blowgun", "weapon.short_launcher", "weapon.chakram", "weapon.returning_thrower"] },
    { id: "weapon-flexible", zh: "鞭链、钩具与捕缚", en: "Flexible, hooked & capture weapons", types: ["weapon.flexible", "weapon.chain", "weapon.soft", "weapon.hook", "weapon.climbing_blade", "weapon.net", "weapon.capture"] },
    { id: "weapon-siege", zh: "攻城、爆炸与陷阱", en: "Siege, explosives & traps", types: ["weapon.siege", "weapon.siege_engine", "weapon.explosive", "weapon.alchemical", "weapon.trap", "weapon.deployable", "weapon.sapper", "weapon.siege_tool"] },
    { id: "weapon-other", zh: "其他武器", en: "Other weapons", types: ["weapon.other"] }
  ]),
  "Armor & protection": Object.freeze([
    { id: "armor-body", zh: "身体护甲", en: "Body armor", types: ["armor.heavy", "armor.plate", "armor.medium", "armor.scale", "armor.light", "armor.leather", "armor.underlayer", "armor.padding", "armor.unspecified", "armor.gorget", "armor.neck_guard"] },
    { id: "armor-shield", zh: "盾牌与头部防护", en: "Shields & head protection", types: ["armor.shield", "armor.buckler", "armor.arm_shield", "armor.head", "armor.faceguard", "armor.mask", "armor.mask_guard"] },
    { id: "armor-limb", zh: "局部护甲与披挂", en: "Limb armor & protective wear", types: ["armor.accessory", "armor.protective_accessory", "armor.bracer", "armor.wrist", "armor.cape", "armor.cloak", "armor.shoulder", "armor.shoulder_guard", "armor.leg", "armor.greaves", "armor.boot", "armor.combat_boot"] },
    { id: "armor-ward", zh: "法术护具与结界器", en: "Wards & magical protection", types: ["armor.ward", "armor.ward_device", "armor.amulet", "armor.personal_charm", "armor.mirror", "armor.anti_curse_plate"] },
    { id: "armor-hazard", zh: "环境、作业与坐骑防护", en: "Hazard & mount protection", types: ["armor.hazard", "armor.work_protection", "armor.mount", "armor.beast", "armor.barding", "armor.beast_cover", "armor.rain", "armor.moisture", "armor.salt_spray", "armor.fire", "armor.fire_resistant"] }
  ])
});

const magicCircleDefinitions = Object.freeze([
  { circle: 1, zh: "一环 · 常见", en: "Circle I · Common" },
  { circle: 2, zh: "二环 · 常见", en: "Circle II · Common" },
  { circle: 3, zh: "三环 · 稳定", en: "Circle III · Uncommon" },
  { circle: 4, zh: "四环 · 稳定", en: "Circle IV · Uncommon" },
  { circle: 5, zh: "五环 · 稀有", en: "Circle V · Rare" },
  { circle: 6, zh: "六环 · 稀有", en: "Circle VI · Rare" },
  { circle: 7, zh: "七环 · 极稀有", en: "Circle VII · Very rare" },
  { circle: 8, zh: "八环 · 传说", en: "Circle VIII · Legendary" }
]);

function magicCircleForEntry(entry) {
  const terms = [...(entry.keys ?? []), ...(entry.secondary_keys ?? [])].join(" ");
  const match = terms.match(/([一二三四五六七八])环/);
  if (match) return "一二三四五六七八".indexOf(match[1]) + 1;
  const order = Number(entry.order);
  return Number.isFinite(order) && order >= 100 && order < 900 ? Math.floor(order / 100) : null;
}

function encyclopediaSubgroups(section, entries) {
  if (section === "Wearables & protection") {
    return [
      {
        id: "wearable-armor",
        label: interfaceLanguage === "zh" ? "防具与护具" : "Armor & protective gear",
        entries: entries.filter((entry) => entry.record?.fields?.category === "Armor & protection")
      },
      {
        id: "wearable-clothing",
        label: interfaceLanguage === "zh" ? "衣着与饰品" : "Clothing & adornment",
        entries: entries.filter((entry) => entry.record?.fields?.category === "Clothing & adornment")
      }
    ].filter((group) => group.entries.length);
  }
  const definitions = encyclopediaItemSubgroups[section];
  if (definitions) {
    return definitions.map((definition) => ({
      ...definition,
      label: interfaceLanguage === "zh" ? definition.zh : definition.en,
      entries: entries.filter((entry) => definition.types.includes(entry.baseTypeId))
    })).filter((group) => group.entries.length);
  }
  if (section === "Magic & rituals") {
    return magicCircleDefinitions.map((definition) => ({
      id: `magic-circle:${definition.circle}`,
      label: interfaceLanguage === "zh" ? definition.zh : definition.en,
      entries: entries.filter((entry) => magicCircleForEntry(entry) === definition.circle)
    })).filter((group) => group.entries.length);
  }
  return null;
}

function openLoreEntry(data, entry, clearSearch = false) {
  if (clearSearch) {
    universeLoreQuery = "";
    universeLoreSearch.value = "";
  }
  selectedUniverseLoreCategory = entry.category || "General";
  selectedUniverseLoreGroup = encyclopediaGroupForSection(selectedUniverseLoreCategory);
  selectedUniverseLoreEntryId = entry.id;
  expandedUniverseLoreSubgroupId = null;
  collapsedUniverseLoreSubgroups.clear();
  renderUniverseLore(data);
}

function appendCrossLinkedLore(container, selectedEntry, entries, data) {
  const text = selectedEntry.content ?? "";
  const candidates = entries
    .filter((entry) => entry.id !== selectedEntry.id && entry.title?.length >= 2 && text.includes(entry.title))
    .sort((left, right) => right.title.length - left.title.length);
  let cursor = 0;
  while (cursor < text.length) {
    let match = null;
    for (const entry of candidates) {
      const index = text.indexOf(entry.title, cursor);
      if (index < 0) continue;
      if (!match || index < match.index || (index === match.index && entry.title.length > match.entry.title.length)) {
        match = { index, entry };
      }
    }
    if (!match) {
      container.append(document.createTextNode(text.slice(cursor)));
      break;
    }
    if (match.index > cursor) container.append(document.createTextNode(text.slice(cursor, match.index)));
    const link = document.createElement("button");
    link.type = "button";
    link.className = "lore-inline-link";
    link.textContent = match.entry.title;
    link.title = interfaceLanguage === "zh" ? "打开相关百科条目" : "Open related encyclopedia entry";
    link.addEventListener("click", () => openLoreEntry(data, match.entry, true));
    container.append(link);
    cursor = match.index + match.entry.title.length;
  }
  if (!text) container.textContent = interfaceLanguage === "zh" ? "此条目尚无正文。" : "This entry has no body text yet.";
}

function relatedLoreEntries(selectedEntry, entries) {
  const selectedTerms = new Set([...(selectedEntry.keys ?? []), ...(selectedEntry.secondary_keys ?? [])]
    .map((term) => String(term).toLocaleLowerCase()));
  const selectedContent = String(selectedEntry.content ?? "").toLocaleLowerCase();
  const selectedTitle = String(selectedEntry.title ?? "").toLocaleLowerCase();
  return entries.filter((entry) => entry.id !== selectedEntry.id).map((entry) => {
    const content = String(entry.content ?? "").toLocaleLowerCase();
    const title = String(entry.title ?? "").toLocaleLowerCase();
    const terms = new Set([...(entry.keys ?? []), ...(entry.secondary_keys ?? [])]
      .map((term) => String(term).toLocaleLowerCase()));
    let score = entry.category === selectedEntry.category ? 1 : 0;
    if (title && selectedContent.includes(title)) score += 6;
    if (selectedTitle && content.includes(selectedTitle)) score += 5;
    for (const term of selectedTerms) if (term.length >= 2 && terms.has(term)) score += 2;
    return { entry, score };
  }).filter((item) => item.score > 0)
    .sort((left, right) => right.score - left.score || left.entry.title.localeCompare(right.entry.title))
    .slice(0, 4).map((item) => item.entry);
}

function itemTypeLoreEntry(type) {
  const abilityRelation = type.baseline?.ability_relation ?? "";
  const subcategory = type.category;
  return {
    id: `item-type:${type.id}`, category: type.group ?? type.category, title: type.label,
    reference: type.reference, baseTypeId: type.id, isBaseType: true,
    abilityRelation,
    record: { record_type: "item_class", canonical_name: type.label, aliases: type.signals ?? [], summary: type.baseline?.use ?? "", status: "schema", fields: { base_type_id: type.id, category: subcategory, group: type.group ?? subcategory }, relations: [] },
    content: `${type.baseline?.use ?? ""} ${type.baseline?.limits ?? ""} ${abilityRelation}`,
    keys: [...(type.signals ?? []), ...(abilityRelation ? ["能力", "物品赋能", "魔法物品"] : [])]
  };
}

function appendRecordMetadata(container, entry) {
  const record = entry.record && typeof entry.record === "object" ? entry.record : null;
  if (!record || (!record.record_type && !record.summary && !record.fields && !record.relations)) return;
  const section = document.createElement("section");
  section.className = "encyclopedia-record";
  const heading = document.createElement("h4");
  heading.textContent = interfaceLanguage === "zh" ? "数据库记录" : "Database record";
  section.append(heading);
  const grid = document.createElement("dl");
  grid.className = "encyclopedia-record-grid";
  const labels = {
    record_type: interfaceLanguage === "zh" ? "记录类型" : "Record type",
    canonical_name: interfaceLanguage === "zh" ? "规范名称" : "Canonical name",
    aliases: interfaceLanguage === "zh" ? "别名" : "Aliases",
    summary: interfaceLanguage === "zh" ? "摘要" : "Summary",
    status: interfaceLanguage === "zh" ? "状态" : "Status",
    region: interfaceLanguage === "zh" ? "区域" : "Region",
    tags: interfaceLanguage === "zh" ? "标签" : "Tags"
  };
  const rows = ["record_type", "canonical_name", "aliases", "summary", "status", "region", "tags"]
    .filter((key) => record[key] !== undefined && record[key] !== null && record[key] !== "");
  const addRow = (key, value) => {
    const term = document.createElement("dt");
    term.textContent = labels[key] ?? key.replaceAll("_", " ");
    const definition = document.createElement("dd");
    definition.textContent = Array.isArray(value) ? value.join("、") : String(value);
    grid.append(term, definition);
  };
  rows.forEach((key) => addRow(key, record[key]));
  const fields = record.fields && typeof record.fields === "object" ? record.fields : {};
  Object.entries(fields).forEach(([key, value]) => addRow(key, value));
  grid.querySelectorAll("dt").forEach((term) => { if (!labels[term.textContent]) term.textContent = term.textContent.replaceAll("_", " "); });
  section.append(grid);
  const relations = Array.isArray(record.relations) ? record.relations.filter((item) => item && item.target) : [];
  if (relations.length) {
    const relationHeading = document.createElement("h5");
    relationHeading.textContent = interfaceLanguage === "zh" ? "关系" : "Relations";
    const relationList = document.createElement("div");
    relationList.className = "encyclopedia-record-relations";
    for (const relation of relations) {
      const target = (loadedUniverseLore?.entries ?? []).find((candidate) => candidate.title === relation.target)
        ?? (loadedUniverseLore?.entries ?? []).find((candidate) => candidate.title?.includes(relation.target));
      const control = document.createElement(target ? "button" : "span");
      control.textContent = `${relation.type ?? "related"} · ${relation.target}`;
      if (target) {
        control.type = "button";
        control.addEventListener("click", () => openLoreEntry(loadedUniverseLore, target, true));
      }
      relationList.append(control);
    }
    section.append(relationHeading, relationList);
  }
  container.append(section);
}

function renderUniverseLore(data) {
  loadedUniverseLore = data;
  universeBible.hidden = false;
  universeTitle.textContent = localized(data.universe.title);
  document.querySelector("#universe-description").textContent = localized(data.universe.description || "Shared background for every world in this universe.");
  const itemCatalog = data.item_catalog ?? { types: [], examples: {} };
  const typeEntries = itemCatalog.types.map(itemTypeLoreEntry);
  const typeById = new Map(typeEntries.map((entry) => [entry.baseTypeId, entry]));
  const rarityById = new Map((itemCatalog.rarities ?? []).map((entry) => [entry.id, entry]));
  const rarityLabelFor = (example) => {
    const rarity = rarityById.get(example?.rarity ?? example?.id) ?? example;
    return interfaceLanguage === "zh" ? (rarity?.label ?? example?.rarity_label ?? "普通／常见")
      : (rarity?.label_en ?? example?.rarity_label ?? "Common");
  };
  const allEntries = [...data.entries, ...typeEntries];
  const allSections = [...encyclopediaSections];
  for (const entry of data.entries) {
    const section = entry.category || "General";
    if (!allSections.includes(section)) allSections.push(section);
  }
  const entriesBySection = new Map(allSections.map((section) => [section, []]));
  for (const entry of data.entries) entriesBySection.get(entry.category || "General")?.push(entry);
  // Each section owns an explicit source. Item categories are stable schemas;
  // story, rules, and spell pages are ordinary World Bible entries.
  const entriesForSection = (section) => encyclopediaSection(section).source === "item-types"
    ? typeEntries.filter((entry) => entry.category === section)
    : (entriesBySection.get(section) ?? []);
  const entriesForGroup = (group) => allSections
    .filter((section) => encyclopediaGroupForSection(section) === group.id)
    .flatMap((section) => entriesForSection(section));
  const activeGroup = encyclopediaGroup(selectedUniverseLoreGroup);
  const sections = allSections.filter((section) => encyclopediaGroupForSection(section) === activeGroup.id);
  if (!sections.includes(selectedUniverseLoreCategory)) {
    selectedUniverseLoreCategory = sections.find((section) => entriesForSection(section).length) ?? sections[0];
  }

  universeLoreGroups.replaceChildren();
  for (const group of encyclopediaGroups) {
    const control = document.createElement("button");
    control.type = "button";
    control.className = `encyclopedia-tab${group.id === activeGroup.id ? " active" : ""}`;
    control.setAttribute("role", "tab");
    control.setAttribute("aria-selected", group.id === activeGroup.id ? "true" : "false");
    const groupCount = entriesForGroup(group).length;
    control.textContent = `${localized(group.label)} · ${groupCount}`;
    control.addEventListener("click", () => {
      selectedUniverseLoreGroup = group.id;
      const nextSections = allSections.filter((section) => encyclopediaGroupForSection(section) === group.id);
      selectedUniverseLoreCategory = nextSections.find((section) => entriesForSection(section).length) ?? nextSections[0];
      selectedUniverseLoreEntryId = entriesForSection(selectedUniverseLoreCategory)[0]?.id ?? null;
      collapsedUniverseLoreCategories.clear();
      collapsedUniverseLoreSubgroups.clear();
      expandedUniverseLoreSubgroupId = null;
      universeLoreQuery = "";
      universeLoreSearch.value = "";
      renderUniverseLore(data);
    });
    universeLoreGroups.append(control);
  }

  const query = universeLoreQuery.trim().toLocaleLowerCase();
  const searchResults = query ? allEntries.map((entry) => ({ entry, score: loreSearchScore(entry, query) }))
    .filter((item) => item.score >= 0)
    .sort((left, right) => right.score - left.score || left.entry.title.localeCompare(right.entry.title))
    .map((item) => item.entry) : [];
  let activeEntries = query ? searchResults : entriesForSection(selectedUniverseLoreCategory);
  if (!activeEntries.some((entry) => entry.id === selectedUniverseLoreEntryId)) {
    selectedUniverseLoreEntryId = activeEntries[0]?.id ?? null;
  }
  const activeGroupEntryCount = entriesForGroup(activeGroup).length;
  const magicEntryCount = entriesForSection("Magic & rituals").length;
  universeLoreSearchStatus.textContent = query
    ? (interfaceLanguage === "zh" ? `找到 ${searchResults.length} 条匹配记录。` : `${searchResults.length} matching records.`)
    : (interfaceLanguage === "zh"
      ? activeGroup.id === "items" ? `包含 ${typeEntries.length} 类物品与 ${magicEntryCount} 条魔法及仪式条目；具体物品的来历和性质会在故事中逐步显现。`
        : `${localized(activeGroup.label)}共有 ${activeGroupEntryCount} 条百科内容。`
      : `${activeGroupEntryCount} entries in ${localized(activeGroup.label)}.`);

  universeLoreCategories.replaceChildren();
  if (query) {
    const branch = document.createElement("section");
    branch.className = "encyclopedia-branch active";
    const heading = document.createElement("div");
    heading.className = "encyclopedia-chapter search-heading";
    heading.textContent = interfaceLanguage === "zh" ? `搜索结果 · ${searchResults.length}` : `Search results · ${searchResults.length}`;
    branch.append(heading);
    const entryList = document.createElement("div");
    entryList.className = "encyclopedia-entry-menu";
    for (const entry of searchResults) {
      const item = document.createElement("button");
      item.type = "button";
      item.className = `encyclopedia-entry-link${entry.id === selectedUniverseLoreEntryId ? " active" : ""}`;
      item.textContent = `${entry.title} · ${localized(entry.category || "General")}`;
      item.addEventListener("click", () => openLoreEntry(data, entry));
      entryList.append(item);
    }
    branch.append(entryList);
    universeLoreCategories.append(branch);
  } else {
    for (const section of sections) {
      const entries = entriesForSection(section);
      const isSelected = section === selectedUniverseLoreCategory;
      const isExpanded = isSelected && !collapsedUniverseLoreCategories.has(section);
      const branch = document.createElement("section");
      branch.className = `encyclopedia-branch${isSelected ? " active" : ""}${isExpanded ? " expanded" : " collapsed"}`;
      const chapter = document.createElement("button");
      chapter.type = "button";
      chapter.className = "encyclopedia-chapter";
      chapter.setAttribute("aria-current", isSelected ? "page" : "false");
      chapter.setAttribute("aria-expanded", isExpanded ? "true" : "false");
      const chapterLabel = document.createElement("span");
      chapterLabel.textContent = localized(section);
      const count = document.createElement("small");
      count.textContent = String(entries.length);
      chapter.append(chapterLabel, count);
      chapter.addEventListener("click", () => {
        if (selectedUniverseLoreCategory === section) {
          if (collapsedUniverseLoreCategories.has(section)) collapsedUniverseLoreCategories.delete(section);
          else collapsedUniverseLoreCategories.add(section);
        } else {
          selectedUniverseLoreCategory = section;
          selectedUniverseLoreEntryId = entries[0]?.id ?? null;
          collapsedUniverseLoreCategories.delete(section);
          collapsedUniverseLoreSubgroups.clear();
          expandedUniverseLoreSubgroupId = null;
        }
        renderUniverseLore(data);
      });
      branch.append(chapter);
      if (isExpanded && entries.length) {
        const subgroups = encyclopediaSubgroups(section, entries);
        if (!subgroups) {
          const entryList = document.createElement("div");
          entryList.className = "encyclopedia-entry-menu";
          for (const entry of entries) {
            const item = document.createElement("button");
            item.type = "button";
            item.className = `encyclopedia-entry-link${entry.id === selectedUniverseLoreEntryId ? " active" : ""}`;
            item.textContent = entry.title;
            item.setAttribute("aria-current", entry.id === selectedUniverseLoreEntryId ? "page" : "false");
            item.addEventListener("click", () => openLoreEntry(data, entry));
            entryList.append(item);
          }
          branch.append(entryList);
        } else {
          const selectedSubgroup = subgroups.find((group) => group.entries.some((entry) => entry.id === selectedUniverseLoreEntryId));
          const expandedSubgroupId = expandedUniverseLoreSubgroupId ?? selectedSubgroup?.id ?? subgroups[0]?.id;
          const subgroupList = document.createElement("div");
          subgroupList.className = `encyclopedia-subgroups${subgroups.length > 1 ? " has-groups" : ""}`;
          for (const subgroup of subgroups) {
          const subgroupBranch = document.createElement("section");
          const subgroupExpanded = subgroups.length === 1 || (expandedSubgroupId === subgroup.id && !collapsedUniverseLoreSubgroups.has(subgroup.id));
          subgroupBranch.className = `encyclopedia-subgroup${subgroupExpanded ? " expanded" : " collapsed"}`;
          const subgroupHeading = document.createElement("button");
          subgroupHeading.type = "button";
          subgroupHeading.className = "encyclopedia-subgroup-heading";
          subgroupHeading.setAttribute("aria-expanded", subgroupExpanded ? "true" : "false");
          const subgroupLabel = document.createElement("span");
          subgroupLabel.textContent = subgroup.label;
          const subgroupCount = document.createElement("small");
          subgroupCount.textContent = String(subgroup.entries.length);
          subgroupHeading.append(subgroupLabel, subgroupCount);
          subgroupHeading.addEventListener("click", () => {
            if (subgroups.length === 1) return;
            if (expandedSubgroupId === subgroup.id && !collapsedUniverseLoreSubgroups.has(subgroup.id)) {
              collapsedUniverseLoreSubgroups.add(subgroup.id);
            } else {
              collapsedUniverseLoreSubgroups.clear();
              expandedUniverseLoreSubgroupId = subgroup.id;
            }
            renderUniverseLore(data);
          });
          subgroupBranch.append(subgroupHeading);
          if (subgroupExpanded) {
            const entryList = document.createElement("div");
            entryList.className = "encyclopedia-entry-menu";
            for (const entry of subgroup.entries) {
              const item = document.createElement("button");
              item.type = "button";
              item.className = `encyclopedia-entry-link${entry.id === selectedUniverseLoreEntryId ? " active" : ""}`;
              item.textContent = entry.title;
              item.setAttribute("aria-current", entry.id === selectedUniverseLoreEntryId ? "page" : "false");
              item.addEventListener("click", () => openLoreEntry(data, entry));
              entryList.append(item);
            }
            subgroupBranch.append(entryList);
          }
            subgroupList.append(subgroupBranch);
          }
          branch.append(subgroupList);
        }
      }
      universeLoreCategories.append(branch);
    }
  }

  universeLoreList.replaceChildren();
  const selectedEntry = activeEntries.find((entry) => entry.id === selectedUniverseLoreEntryId);
  if (!selectedEntry) {
    const empty = document.createElement("p");
    empty.className = "encyclopedia-empty";
    empty.textContent = query
      ? (interfaceLanguage === "zh" ? "没有匹配的百科条目。可以尝试更短的名称或关键词。" : "No encyclopedia entries match. Try a shorter name or keyword.")
      : (interfaceLanguage === "zh" ? `${localized(selectedUniverseLoreCategory)}中还没有条目。` : `No entries yet in ${selectedUniverseLoreCategory}.`);
    universeLoreList.append(empty);
    return;
  }
  const row = document.createElement("article");
  row.className = "encyclopedia-entry";
  const meta = document.createElement("div");
  meta.className = "encyclopedia-entry-meta";
  const category = document.createElement("span");
  category.textContent = localized(selectedEntry.category || "General");
  if (selectedEntry.isBaseType) {
    const level = document.createElement("span");
    level.textContent = interfaceLanguage === "zh" ? "物品类型" : "Item type";
    meta.append(category, level);
    if (selectedEntry.abilityRelation) {
      const abilityMarker = document.createElement("span");
      abilityMarker.textContent = interfaceLanguage === "zh" ? "能力相关" : "Ability-related";
      meta.append(abilityMarker);
    }
  } else {
    const position = document.createElement("span");
    position.textContent = `${activeEntries.findIndex((entry) => entry.id === selectedEntry.id) + 1} / ${activeEntries.length}`;
    meta.append(category, position);
  }
  const label = document.createElement("h3");
  label.textContent = selectedEntry.title;
  const body = document.createElement("div");
  body.className = "lore-body";
  if (!selectedEntry.isBaseType) {
    appendCrossLinkedLore(body, selectedEntry, data.entries, data);
  }
  row.append(meta, label);
  if (body.textContent || body.children.length) row.append(body);
  // Structured records remain available to search and narrator retrieval, but
  // their storage fields are an implementation detail rather than player UI.
  const baseTypeId = selectedEntry.baseTypeId;
  const baseType = itemCatalog.types.find((type) => type.id === baseTypeId);
  if (baseType) {
    const baseline = document.createElement("div");
    baseline.className = "encyclopedia-type-baseline";
    const heading = document.createElement("h4");
    heading.textContent = selectedEntry.isBaseType ? "使用与限制" : `相关类型 · ${baseType.label}`;
    const use = document.createElement("p");
    use.textContent = baseType.baseline?.use ?? "";
    const limits = document.createElement("p");
    limits.textContent = baseType.baseline?.limits ?? "";
    baseline.append(heading, use, limits);
    if (selectedEntry.abilityRelation) {
      const abilityHeading = document.createElement("h4");
      abilityHeading.textContent = interfaceLanguage === "zh" ? "与能力的关系" : "Relationship to abilities";
      const abilityRelation = document.createElement("p");
      abilityRelation.className = "item-ability-relation";
      abilityRelation.textContent = selectedEntry.abilityRelation;
      baseline.append(abilityHeading, abilityRelation);
    }
    row.append(baseline);
  }
  if (selectedEntry.isBaseType) {
    const rarityGuide = document.createElement("section");
    rarityGuide.className = "item-rarity-guide";
    const heading = document.createElement("h4");
    heading.textContent = interfaceLanguage === "zh"
      ? "等级参考 · 仅列少量示例，不代表完整清单"
      : "Rarity guide · A few examples, not a complete list";
    rarityGuide.append(heading);
    for (const rarity of itemCatalog.rarities ?? []) {
      const rarityRow = document.createElement("div");
      rarityRow.className = "item-rarity-guide-row";
      const name = document.createElement("strong");
      name.className = "item-rarity";
      name.dataset.rarity = rarity.id;
      name.textContent = rarityLabelFor(rarity);
      const guide = baseType.rarity_guide?.[rarity.id];
      const details = document.createElement("div");
      details.className = "item-rarity-guide-details";
      const description = document.createElement("p");
      const text = interfaceLanguage === "zh"
        ? (guide?.description ?? rarity.description)
        : (rarity.description_en ?? rarity.description);
      const instanceNote = rarity.instance_only
        ? (interfaceLanguage === "zh" ? "仅用于已经确立的具体具名物品。" : "Only for an established named individual item.")
        : "";
      description.textContent = `${text}${instanceNote ? ` ${instanceNote}` : ""}`;
      details.append(description);
      if (guide?.examples?.length) {
        const examples = document.createElement("p");
        examples.className = "item-rarity-examples";
        examples.textContent = `${interfaceLanguage === "zh" ? "少量示例（非完整清单）" : "A few examples (not exhaustive)"}：${guide.examples.join("；")}`;
        details.append(examples);
      }
      rarityRow.append(name, details);
      rarityGuide.append(rarityRow);
    }
    row.append(rarityGuide);
  }
  const relatedEntries = selectedEntry.isBaseType ? [] : relatedLoreEntries(selectedEntry, data.entries);
  if (relatedEntries.length) {
    const related = document.createElement("aside");
    related.className = "encyclopedia-related";
    const relatedTitle = document.createElement("h4");
    relatedTitle.textContent = interfaceLanguage === "zh" ? "相关条目" : "Related entries";
    const relatedLinks = document.createElement("div");
    for (const entry of relatedEntries) {
      const control = document.createElement("button");
      control.type = "button";
      control.textContent = entry.title;
      control.addEventListener("click", () => openLoreEntry(data, entry, true));
      relatedLinks.append(control);
    }
    related.append(relatedTitle, relatedLinks);
    row.append(related);
  }
  universeLoreList.append(row);
}

universeLoreSearch.addEventListener("input", () => {
  universeLoreQuery = universeLoreSearch.value;
  if (loadedUniverseLore) renderUniverseLore(loadedUniverseLore);
});

async function loadUniverseLore() {
  try {
    const response = await fetch(`/api/universe-lore?universe=${encodeURIComponent(selectedUniverseId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read shared lore.");
    renderUniverseLore(data);
  } catch {
    universeBible.hidden = true;
  }
}

function localRequest(path, options = {}) {
  const method = String(options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers ?? {});
  if (["POST", "PATCH", "DELETE"].includes(method)) {
    headers.set("x-secret-fire-request", "1");
    if (!headers.has("content-type")) headers.set("content-type", "application/json");
  }
  return fetch(path, { ...options, method, headers });
}

async function saveRequest(path, options) {
  const response = await localRequest(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error ?? "The save operation did not complete.");
  return data;
}

function actionButton(label, handler, danger = false) {
  const control = document.createElement("button");
  control.type = "button";
  control.textContent = label;
  if (danger) control.className = "danger";
  control.addEventListener("click", () => void handler(control));
  return control;
}

function renderSaveState(state) {
  void loadPossessions();
  void loadCast();
  void loadChapters();
  timelineStatus.textContent = interfaceLanguage === "zh"
    ? "当前进度已保存在本机。恢复存档点时会建立另一条时间线，不会覆盖现在的故事。"
    : "Your current progress is saved locally. Restoring a save point creates another timeline without overwriting this story.";
  checkpointList.replaceChildren();
  branchList.replaceChildren();
  if (!state.checkpoints.length) {
    const empty = document.createElement("li");
    empty.textContent = interfaceLanguage === "zh" ? "尚未创建存档点。" : "No save points yet.";
    checkpointList.append(empty);
  }
  for (const checkpoint of state.checkpoints) {
    const row = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = checkpoint.name;
    const details = document.createElement("small");
    details.textContent = interfaceLanguage === "zh" ? `第 ${checkpoint.turn_number} 回合` : `Turn ${checkpoint.turn_number}`;
    row.append(label, details);
    row.append(actionButton(localized("Restore"), async () => {
      if (!confirm(`Restore “${checkpoint.name}” as a new timeline? Your current timeline will remain available.`)) return;
      renderSaveState(await saveRequest(`/api/checkpoints/${encodeURIComponent(checkpoint.id)}/restore`, { method: "POST" }));
      void loadTimeline();
    }));
    row.append(actionButton(interfaceLanguage === "zh" ? "移除" : "Remove", async () => {
      if (!confirm(`Remove the marker “${checkpoint.name}”? The story itself will remain.`)) return;
      renderSaveState(await saveRequest(`/api/checkpoints/${encodeURIComponent(checkpoint.id)}`, { method: "DELETE" }));
    }, true));
    checkpointList.append(row);
  }
  for (const [branchIndex, branch] of state.branches.entries()) {
    const row = document.createElement("li");
    const label = document.createElement("span");
    const active = branch.name === state.active_branch;
    label.textContent = active
      ? (interfaceLanguage === "zh" ? "当前时间线" : "Current timeline")
      : (interfaceLanguage === "zh" ? `其他时间线 ${branchIndex + 1}` : `Other timeline ${branchIndex + 1}`);
    if (active) label.className = "active";
    const details = document.createElement("small");
    details.textContent = interfaceLanguage === "zh" ? `从第 ${branch.base_turn_number} 回合分开` : `Diverged after turn ${branch.base_turn_number}`;
    row.append(label, details);
    if (!active) {
      row.append(actionButton(interfaceLanguage === "zh" ? "进入" : "Open", async () => {
        renderSaveState(await saveRequest(`/api/branches/${encodeURIComponent(branch.name)}/checkout`, { method: "POST" }));
        void loadTimeline();
      }));
      row.append(actionButton(interfaceLanguage === "zh" ? "删除" : "Delete", async () => {
        if (!confirm(`Permanently delete timeline “${branch.name}”? Its local storage will be reclaimed.`)) return;
        renderSaveState(await saveRequest(`/api/branches/${encodeURIComponent(branch.name)}`, { method: "DELETE" }));
      }, true));
    }
    branchList.append(row);
  }
}

async function loadSaveState() {
  if (!activeWorldId) return;
  try {
    renderSaveState(await saveRequest("/api/save-state"));
  } catch (error) {
    timelineStatus.textContent = error instanceof Error ? `Could not read save data: ${error.message}` : "Could not read save data.";
  }
}

async function showChapterSource(chapter) {
  try {
    const response = await fetch(`/api/chapters/source?start=${chapter.start_turn}&end=${chapter.end_turn}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read source turns.");
    chapterSourceText.textContent = data.turns.map((turn) =>
      `${interfaceLanguage === "zh" ? "回合" : "Turn"} ${turn.turn_number}\n${interfaceLanguage === "zh" ? "玩家" : "Player"}：${turn.player_action}\n${interfaceLanguage === "zh" ? "结果" : "Outcome"}：${turn.narration}`
    ).join("\n\n");
    chapterSourceReview.hidden = false;
    chapterSourceReview.open = true;
    chapterSourceReview.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    chapterStatus.textContent = error instanceof Error ? error.message : "Could not read source turns.";
  }
}

function renderChapters(data) {
  loadedChapters = data;
  chapterList.replaceChildren();
  const available = data.maximum_turn > 0;
  chapterStart.disabled = !available;
  chapterEnd.disabled = !available;
  chapterForm.querySelector("button[type=submit]").disabled = !available;
  if (available) {
    chapterStart.min = String(data.minimum_turn);
    chapterStart.max = String(data.maximum_turn);
    chapterEnd.min = String(data.minimum_turn);
    chapterEnd.max = String(data.maximum_turn);
    if (document.activeElement !== chapterStart) chapterStart.value = String(data.suggested_start);
    if (document.activeElement !== chapterEnd) chapterEnd.value = String(data.suggested_end);
    chapterStatus.textContent = interfaceLanguage === "zh"
      ? `当前时间线共有 ${data.maximum_turn} 个故事回合；章节一次最多覆盖 50 回合。`
      : `${data.maximum_turn} story turn(s) on this timeline; one chapter can cover up to 50 turns.`;
  } else {
    chapterStart.value = "";
    chapterEnd.value = "";
    chapterStatus.textContent = localized("Play at least one story turn to create a chapter.");
  }
  if (!data.chapters.length) {
    const empty = document.createElement("p");
    empty.className = "save-help";
    empty.textContent = interfaceLanguage === "zh" ? "尚未创建章节摘要。" : "No chapter summaries yet.";
    chapterList.append(empty);
    return;
  }
  for (const chapter of data.chapters) {
    const card = document.createElement("article");
    card.className = `chapter-card ${chapter.status}`;
    const meta = document.createElement("div");
    meta.className = "chapter-meta";
    const statusBadge = document.createElement("span");
    statusBadge.textContent = chapter.status === "approved"
      ? (interfaceLanguage === "zh" ? "已确认" : "Approved")
      : (interfaceLanguage === "zh" ? "草稿" : "Draft");
    const range = document.createElement("span");
    range.textContent = interfaceLanguage === "zh"
      ? `回合 ${chapter.start_turn}–${chapter.end_turn}`
      : `Turns ${chapter.start_turn}–${chapter.end_turn}`;
    const audit = document.createElement("span");
    audit.className = chapter.source_matches ? "verified" : "mismatch";
    audit.textContent = chapter.source_matches
      ? (interfaceLanguage === "zh" ? "来源已校验" : "Source verified")
      : (interfaceLanguage === "zh" ? "来源已变化" : "Source changed");
    meta.append(statusBadge, range, audit);
    const title = document.createElement("input");
    title.value = chapter.title;
    title.maxLength = 120;
    title.setAttribute("aria-label", interfaceLanguage === "zh" ? "章节标题" : "Chapter title");
    const summary = document.createElement("textarea");
    summary.value = chapter.summary;
    summary.rows = 8;
    summary.maxLength = 12000;
    summary.setAttribute("aria-label", interfaceLanguage === "zh" ? "章节摘要" : "Chapter summary");
    const actions = document.createElement("div");
    actions.className = "chapter-actions";
    const source = actionButton(interfaceLanguage === "zh" ? "核对原文" : "Review source", () => showChapterSource(chapter));
    const save = actionButton(interfaceLanguage === "zh" ? "保存修改" : "Save edits", async (control) => {
      control.disabled = true;
      try {
        renderChapters(await saveRequest(`/api/chapters/${encodeURIComponent(chapter.id)}`, {
          method: "PATCH", headers: { "content-type": "application/json" },
          body: JSON.stringify({ title: title.value.trim(), summary: summary.value.trim(), status: chapter.status })
        }));
      } catch (error) {
        chapterStatus.textContent = error instanceof Error ? error.message : "Could not save chapter.";
      } finally {
        control.disabled = false;
      }
    });
    const approval = actionButton(chapter.status === "approved"
      ? (interfaceLanguage === "zh" ? "退回草稿" : "Return to draft")
      : (interfaceLanguage === "zh" ? "确认摘要" : "Approve"), async (control) => {
      control.disabled = true;
      try {
        renderChapters(await saveRequest(`/api/chapters/${encodeURIComponent(chapter.id)}`, {
          method: "PATCH", headers: { "content-type": "application/json" },
          body: JSON.stringify({
            title: title.value.trim(), summary: summary.value.trim(),
            status: chapter.status === "approved" ? "draft" : "approved"
          })
        }));
      } catch (error) {
        chapterStatus.textContent = error instanceof Error ? error.message : "Could not update chapter approval.";
      } finally {
        control.disabled = false;
      }
    });
    approval.disabled = !chapter.source_matches;
    const remove = actionButton(interfaceLanguage === "zh" ? "删除" : "Delete", async () => {
      const message = interfaceLanguage === "zh"
        ? "删除这份章节摘要？原始故事回合不会受到影响。"
        : "Delete this chapter summary? Original story turns will not be changed.";
      if (!confirm(message)) return;
      try {
        renderChapters(await saveRequest(`/api/chapters/${encodeURIComponent(chapter.id)}`, { method: "DELETE" }));
      } catch (error) {
        chapterStatus.textContent = error instanceof Error ? error.message : "Could not delete chapter.";
      }
    }, true);
    actions.append(source, save, approval, remove);
    card.append(meta, title, summary, actions);
    chapterList.append(card);
  }
}

async function loadChapters() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/chapters");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read chapter summaries.");
    renderChapters(data);
  } catch (error) {
    chapterStatus.textContent = error instanceof Error ? error.message : "Could not read chapter summaries.";
  }
}

function resetPossessionForm() {
  possessionForm.reset();
  possessionId.value = "";
  possessionCategory.value = "ordinary";
  possessionType.value = "";
  possessionRarity.value = "common";
  possessionRarity.dataset.known = "true";
  possessionRarity.dataset.internalRarity = "common";
  possessionRarity.dataset.basis = "";
  possessionTypeHint.textContent = "";
  possessionStatus.value = "carried";
  possessionImportance.value = "5";
  possessionQuantity.value = "1";
  possessionHolder.value = "player";
  possessionPlace.input.value = "";
}

function rebuildHolderOptions(selected = possessionHolder.value || "player") {
  possessionHolder.replaceChildren();
  const options = [["player", interfaceLanguage === "zh" ? "你" : "You"], ["world", interfaceLanguage === "zh" ? "留在某处" : "At a place"]];
  for (const person of loadedCast?.people ?? []) options.push([person.id, person.name]);
  if (selected && !options.some(([id]) => id === selected)) options.push([selected, interfaceLanguage === "zh" ? "其他／原记录" : "Other / previous record"]);
  for (const [id, name] of options) {
    const option = document.createElement("option");
    option.value = id;
    option.textContent = name;
    possessionHolder.append(option);
  }
  possessionHolder.value = selected;
}

function setPossessionForm(item) {
  possessionId.value = item.id ?? "";
  possessionName.value = item.name ?? "";
  possessionCategory.value = item.category ?? "ordinary";
  possessionType.value = item.base_type_id ?? "";
  possessionRarity.dataset.internalRarity = item.rarity ?? "common";
  possessionRarity.value = item.rarity_known === false ? "unidentified" : (item.rarity ?? "common");
  possessionRarity.dataset.known = item.rarity_known === false ? "false" : "true";
  possessionRarity.dataset.basis = item.rarity_basis ?? "";
  possessionTypeHint.textContent = item.base_type_label
    ? `${interfaceLanguage === "zh" ? "基础类别" : "Base category"}：${item.base_type_label}` : "";
  possessionStatus.value = item.status ?? "carried";
  possessionDescription.value = item.description ?? "";
  possessionPurpose.value = item.known_purpose ?? "";
  possessionImportance.value = item.importance ?? 5;
  possessionQuantity.value = item.quantity ?? 1;
  possessionEquippedAs.value = item.equipped_as ?? "";
  rebuildHolderOptions(item.holder ?? "player");
  possessionPlace.input.value = item.location ?? "";
  document.querySelector("#possessions-drawer").open = true;
  possessionEditor.open = true;
  possessionName.focus();
  if (!possessionType.value) void suggestPossessionType();
}

async function loadItemTypes() {
  const response = await fetch("/api/item-types");
  const data = await response.json();
  if (!response.ok) throw new Error(data.error ?? "Could not load item types.");
  availableItemTypes = data.types ?? [];
  availableItemRarities = data.rarities ?? [];
  const selected = possessionType.value;
  possessionType.replaceChildren();
  const empty = document.createElement("option");
  empty.value = "";
  empty.textContent = interfaceLanguage === "zh" ? "请选择或获取建议" : "Choose or get a suggestion";
  possessionType.append(empty);
  for (const category of [...new Set(availableItemTypes.map((item) => item.group ?? item.category))]) {
    const group = document.createElement("optgroup");
    group.label = localized(category);
    for (const item of availableItemTypes.filter((value) => (value.group ?? value.category) === category)) {
      const option = document.createElement("option");
      option.value = item.id;
      option.textContent = item.label;
      group.append(option);
    }
    possessionType.append(group);
  }
  possessionType.value = selected;
  const selectedRarity = possessionRarity.value || "common";
  possessionRarity.replaceChildren();
  const unidentified = document.createElement("option");
  unidentified.value = "unidentified";
  unidentified.textContent = interfaceLanguage === "zh" ? "未鉴定" : "Unidentified";
  possessionRarity.append(unidentified);
  for (const rarity of availableItemRarities) {
    const option = document.createElement("option");
    option.value = rarity.id;
    option.textContent = interfaceLanguage === "zh" ? rarity.label : (rarity.label_en ?? rarity.label);
    option.title = interfaceLanguage === "zh" ? rarity.description : (rarity.description_en ?? rarity.description);
    possessionRarity.append(option);
  }
  possessionRarity.value = selectedRarity === "unidentified" || availableItemRarities.some((rarity) => rarity.id === selectedRarity)
    ? selectedRarity : "common";
}

async function suggestPossessionType() {
  const name = possessionName.value.trim();
  const description = possessionDescription.value.trim();
  if (!name) return;
  try {
    const result = await saveRequest("/api/item-classify", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ name, description })
    });
    if (possessionName.value.trim() !== name || possessionDescription.value.trim() !== description) return;
    possessionType.value = result.base_type_id ?? "";
    possessionRarity.value = result.rarity ?? "common";
    possessionRarity.dataset.known = "true";
    possessionRarity.dataset.internalRarity = result.rarity ?? "common";
    possessionRarity.dataset.basis = "";
    possessionTypeHint.textContent = result.base_type_id
      ? `${interfaceLanguage === "zh" ? "基础类别" : "Base category"}：${result.base_type_label}${result.requires_review ? " · 请确认类别" : ""}`
      : (interfaceLanguage === "zh" ? "无法凭名称判断，请从列表选择基础类别；特殊效果另行记录。" : "Cannot tell from the name; choose a base category. Special effects need separate evidence.");
  } catch (error) {
    possessionTypeHint.textContent = error instanceof Error ? error.message : "Could not suggest a type.";
  }
}

suggestTypeButton.addEventListener("click", () => void suggestPossessionType());
possessionType.addEventListener("change", () => {
  const selected = availableItemTypes.find((item) => item.id === possessionType.value);
  possessionTypeHint.textContent = selected
    ? `${interfaceLanguage === "zh" ? "基础类别" : "Base category"}：${selected.label}`
    : "";
});
possessionRarity.addEventListener("change", () => {
  possessionRarity.dataset.known = possessionRarity.value === "unidentified" ? "false" : "true";
  if (possessionRarity.value !== "unidentified") possessionRarity.dataset.internalRarity = possessionRarity.value;
  possessionRarity.dataset.basis = "";
});

function possessionPayload() {
  return {
    id: possessionId.value,
    name: possessionName.value.trim(), category: possessionCategory.value, status: possessionStatus.value,
    base_type_id: possessionType.value,
    rarity: possessionRarity.value === "unidentified"
      ? (possessionRarity.dataset.internalRarity || "common") : (possessionRarity.value || "common"),
    rarity_known: possessionRarity.dataset.known !== "false",
    rarity_basis: possessionRarity.dataset.basis ?? "",
    description: possessionDescription.value.trim(), known_purpose: possessionPurpose.value.trim(),
    importance: Number(possessionImportance.value), quantity: Number(possessionQuantity.value),
    holder: possessionHolder.value, location: possessionPlace.input.value.trim(),
    equipped_as: possessionEquippedAs.value.trim()
  };
}

async function savePossession(item) {
  const response = await saveRequest("/api/possessions", {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(item)
  });
  renderPossessions(response.possessions);
  return response;
}

function renderPossessionSuggestions(suggestions) {
  pendingPossessionSuggestions = suggestions ?? [];
  possessionSuggestions.replaceChildren();
  possessionSuggestions.hidden = !pendingPossessionSuggestions.length;
  for (const suggestion of pendingPossessionSuggestions) {
    const row = document.createElement("div");
    row.className = "possession-suggestion";
    const text = document.createElement("p");
    text.textContent = suggestion.reason
      ? (interfaceLanguage === "zh" ? `叙事者发现：${suggestion.reason}` : `Narrator noticed: ${suggestion.reason}`)
      : (interfaceLanguage === "zh" ? `叙事者发现了“${suggestion.name}”的变化。` : `Narrator noticed a change to ${suggestion.name}.`);
    const rarity = availableItemRarities.find((entry) => entry.id === suggestion.rarity);
    const rarityDetail = document.createElement("p");
    rarityDetail.className = "possession-suggestion-rarity";
    rarityDetail.textContent = suggestion.rarity_known === false
      ? (interfaceLanguage === "zh" ? "物品性质：未鉴定" : "Nature: Unidentified")
      : `${interfaceLanguage === "zh" ? "等级" : "Rarity"}：${interfaceLanguage === "zh" ? (rarity?.label ?? suggestion.rarity) : (rarity?.label_en ?? suggestion.rarity)}`;
    if (suggestion.rarity_basis && suggestion.rarity_known !== false) {
      rarityDetail.textContent += `${interfaceLanguage === "zh" ? " · 来源依据：" : " · Source: "}${suggestion.rarity_basis}`;
    }
    const actions = document.createElement("div");
    actions.className = "possession-actions";
    const accept = actionButton(interfaceLanguage === "zh" ? "记录到背包" : "Record in backpack", async (control) => {
      control.disabled = true;
      try {
        const classification = await saveRequest("/api/item-classify", {
          method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(suggestion)
        });
        if (!classification.base_type_id) {
          journalStatus.textContent = interfaceLanguage === "zh"
            ? "这个物品暂时无法归入基础类别，因此没有写入背包。"
            : "This item could not be mapped to a base category, so it was not recorded.";
          control.disabled = false;
          return;
        }
        await savePossession({ ...suggestion, base_type_id: classification.base_type_id });
        pendingPossessionSuggestions = pendingPossessionSuggestions.filter((item) => item !== suggestion);
        renderPossessionSuggestions(pendingPossessionSuggestions);
        journalStatus.textContent = interfaceLanguage === "zh" ? "物品已记录到背包。" : "Item recorded in the backpack.";
      } catch (error) {
        journalStatus.textContent = error instanceof Error ? error.message : "Could not record this item.";
        control.disabled = false;
      }
    });
    const ignore = actionButton(interfaceLanguage === "zh" ? "暂不记录" : "Not now", () => {
      pendingPossessionSuggestions = pendingPossessionSuggestions.filter((item) => item !== suggestion);
      renderPossessionSuggestions(pendingPossessionSuggestions);
    }, true);
    actions.append(accept, ignore);
    row.append(text, rarityDetail, actions);
    possessionSuggestions.append(row);
  }
}

function formatCurrency(value) {
  let remaining = Math.max(0, Math.trunc(Number(value) || 0));
  const gold = Math.floor(remaining / 100);
  remaining %= 100;
  const silver = Math.floor(remaining / 10);
  const copper = remaining % 10;
  const parts = [];
  if (gold) parts.push(interfaceLanguage === "zh" ? `${gold} 金` : `${gold} gold`);
  if (silver) parts.push(interfaceLanguage === "zh" ? `${silver} 银` : `${silver} silver`);
  if (copper || !parts.length) parts.push(interfaceLanguage === "zh" ? `${copper} 铜` : `${copper} copper`);
  return parts.join(" · ");
}

function tradeOfferTitle(offer) {
  const itemName = offer.item?.name || offer.item_name || "";
  if (interfaceLanguage === "zh") {
    if (offer.kind === "buy") return `向${offer.counterparty}购买${itemName}${offer.quantity > 1 ? ` ×${offer.quantity}` : ""}`;
    if (offer.kind === "sell") return `向${offer.counterparty}出售${itemName}${offer.quantity > 1 ? ` ×${offer.quantity}` : ""}`;
    if (offer.kind === "reward") return `${offer.counterparty}提供报酬`;
    return `向${offer.counterparty}支付`;
  }
  if (offer.kind === "buy") return `Buy ${itemName}${offer.quantity > 1 ? ` ×${offer.quantity}` : ""} from ${offer.counterparty}`;
  if (offer.kind === "sell") return `Sell ${itemName}${offer.quantity > 1 ? ` ×${offer.quantity}` : ""} to ${offer.counterparty}`;
  if (offer.kind === "reward") return `Receive payment from ${offer.counterparty}`;
  return `Pay ${offer.counterparty}`;
}

function renderResources(data) {
  loadedResources = data;
  resourceWalletLabel.textContent = interfaceLanguage === "zh" ? "钱包" : "Wallet";
  resourceBalance.textContent = formatCurrency(data?.wallet?.balance ?? 0);
  tradeOffers.replaceChildren();
  const offers = (data?.pending_offers ?? []).filter((offer) => !dismissedTradeOffers.has(offer.id));
  tradeOffers.hidden = !offers.length;
  if (offers.length) {
    const heading = document.createElement("h3");
    heading.textContent = interfaceLanguage === "zh" ? "当前报价" : "Current offers";
    tradeOffers.append(heading);
  }
  for (const offer of offers) {
    const row = document.createElement("div");
    row.className = "trade-offer";
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = tradeOfferTitle(offer);
    const price = document.createElement("span");
    price.className = "trade-price";
    price.textContent = formatCurrency(offer.total);
    copy.append(title, price);
    if (offer.reason) {
      const reason = document.createElement("small");
      reason.textContent = offer.reason;
      copy.append(reason);
    }
    const actions = document.createElement("div");
    actions.className = "possession-actions";
    const labels = interfaceLanguage === "zh"
      ? { buy: "买下", sell: "出售", reward: "收下", payment: "支付" }
      : { buy: "Buy", sell: "Sell", reward: "Accept", payment: "Pay" };
    actions.append(actionButton(labels[offer.kind], async (control) => {
      control.disabled = true;
      try {
        const result = await saveRequest("/api/trades", {
          method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ offer_id: offer.id })
        });
        renderPossessions(result.possessions);
        renderResources(result.resources);
        journalStatus.textContent = interfaceLanguage === "zh" ? "交易已完成并写入当前时间线。" : "Trade completed on this timeline.";
      } catch (error) {
        journalStatus.textContent = error instanceof Error ? error.message : "Could not complete this trade.";
        control.disabled = false;
      }
    }));
    actions.append(actionButton(interfaceLanguage === "zh" ? "暂不交易" : "Not now", () => {
      dismissedTradeOffers.add(offer.id);
      renderResources(data);
    }, true));
    row.append(copy, actions);
    tradeOffers.append(row);
  }

  const transactions = [...(data?.transactions ?? [])].reverse().slice(0, 8);
  transactionHistoryLabel.textContent = interfaceLanguage === "zh" ? "最近交易" : "Recent trades";
  transactionHistory.hidden = !transactions.length;
  transactionList.replaceChildren();
  for (const transaction of transactions) {
    const row = document.createElement("li");
    const name = transaction.item_name || transaction.reason || transaction.counterparty;
    const sign = Number(transaction.amount) >= 0 ? "+" : "−";
    row.textContent = `${name} · ${sign}${formatCurrency(Math.abs(Number(transaction.amount) || 0))}`;
    transactionList.append(row);
  }
}

function possessionStatusLabel(status) {
  const labels = interfaceLanguage === "zh"
    ? { equipped: "已装备", stored: "已存放", concealed: "隐蔽携带", given: "已交出", lost: "已遗失", consumed: "已消耗", destroyed: "已毁坏", carried: "随身携带" }
    : { equipped: "Equipped", stored: "Stored", concealed: "Concealed", given: "Given away", lost: "Lost", consumed: "Consumed", destroyed: "Destroyed", carried: "Carried" };
  return labels[status] ?? status;
}

function possessionHolderName(item) {
  if (item.holder === "player") return interfaceLanguage === "zh" ? "你持有" : "Held by you";
  if (item.holder === "world") return interfaceLanguage === "zh" ? "留在某处" : "At a place";
  return (loadedCast?.people ?? []).find((person) => person.id === item.holder)?.name
    || (interfaceLanguage === "zh" ? "去向待确认" : "Holder unconfirmed");
}

function possessionCard(item) {
  const row = document.createElement("li");
  row.className = "record-card item-card";
  const heading = document.createElement("div");
  heading.className = "record-card-heading";
  const identity = document.createElement("div");
  const name = document.createElement("strong");
  name.textContent = `${item.name}${item.quantity > 1 ? ` ×${item.quantity}` : ""}`;
  const meta = document.createElement("small");
  meta.textContent = [possessionHolderName(item), item.location, item.equipped_as].filter(Boolean).join(" · ");
  const badge = document.createElement("span");
  badge.className = "record-card-badge";
  badge.textContent = possessionStatusLabel(item.status);
  identity.append(name, meta);
  heading.append(identity, badge);
  row.append(heading);
  if (item.base_type_label) {
    const type = document.createElement("div");
    type.className = "possession-purpose";
    const rarityLabel = item.rarity_known === false
      ? (interfaceLanguage === "zh" ? "未鉴定" : "Unidentified")
      : (interfaceLanguage === "zh" ? item.rarity_label : (availableItemRarities.find((rarity) => rarity.id === item.rarity)?.label_en ?? item.rarity_label));
    type.textContent = `${interfaceLanguage === "zh" ? "等级" : "Rarity"} · ${rarityLabel || "Common"}　${interfaceLanguage === "zh" ? "基础类别" : "Base category"} · ${item.base_type_label}`;
    type.dataset.rarity = item.rarity_known === false ? "unknown" : (item.rarity ?? "common");
    row.append(type);
    if (item.base_type_id) {
      const reference = actionButton(`${interfaceLanguage === "zh" ? "基础类别" : "Base category"}：${item.base_type_label}`, async () => {
        setView("universe");
        await loadUniverseLore();
        const type = loadedUniverseLore?.item_catalog?.types?.find((entry) => entry.id === item.base_type_id);
        const page = type ? itemTypeLoreEntry(type) : null;
        if (page) openLoreEntry(loadedUniverseLore, page, true);
      });
      row.append(reference);
    }
    if (item.type_baseline?.use) {
      const baseline = document.createElement("details");
      baseline.className = "record-card-more";
      const summary = document.createElement("summary");
      summary.textContent = interfaceLanguage === "zh" ? "基础用途与限制" : "Base use and limits";
      const body = document.createElement("p");
      body.className = "possession-body";
      body.textContent = `${item.type_baseline.use} ${item.type_baseline.limits}`;
      baseline.append(summary, body);
      row.append(baseline);
    }
  }
  if (item.description) {
    const description = document.createElement("details");
    description.className = "record-card-more";
    const summary = document.createElement("summary");
    summary.textContent = interfaceLanguage === "zh" ? "外观与细节" : "Appearance and details";
    const body = document.createElement("p");
    body.className = "possession-body";
    body.textContent = item.description;
    description.append(summary, body);
    row.append(description);
  }
  if (item.known_purpose) {
    const purpose = document.createElement("span");
    purpose.className = "possession-purpose";
    purpose.textContent = `${interfaceLanguage === "zh" ? "已知用途" : "Known use"} · ${item.known_purpose}`;
    row.append(purpose);
  }
  const changes = item.holder !== "player" ? [] : item.status === "equipped"
    ? [["Unequip", "carried"]]
    : item.status === "carried" ? [["Equip", "equipped"]] : [];
  if (changes.length) {
    const actions = document.createElement("div");
    actions.className = "record-quick-actions";
    for (const [label, nextStatus] of changes) {
      actions.append(actionButton(localized(label), async (control) => {
        control.disabled = true;
        try {
          await savePossession({ ...item, status: nextStatus, equipped_as: nextStatus === "equipped" ? item.equipped_as : "" });
          journalStatus.textContent = interfaceLanguage === "zh" ? "背包状态已保存。" : "Backpack updated locally.";
        } catch (error) {
          journalStatus.textContent = error instanceof Error ? error.message : "Could not update this item.";
          control.disabled = false;
        }
      }));
    }
    row.append(actions);
  }
  return row;
}

function appendPossessionSection(container, title, items) {
  if (!items.length) return false;
  const section = document.createElement("section");
  section.className = "possessions-section";
  const heading = document.createElement("h3");
  heading.textContent = localized(title);
  const list = document.createElement("ul");
  for (const item of items) list.append(possessionCard(item));
  section.append(heading, list);
  container.append(section);
  return true;
}

function possessionViewLabel(view, count = 0) {
  const labels = interfaceLanguage === "zh"
    ? { player: "你的背包", party: "小队装备", other: "其他记录" }
    : { player: "Your backpack", party: "Party gear", other: "Other records" };
  return view === "party" && count ? `${labels[view]} · ${count}` : labels[view];
}

function renderPossessionTabs(partyMembers, otherItems) {
  const views = ["player", ...(partyMembers.length ? ["party"] : []), ...(otherItems.length ? ["other"] : [])];
  if (!views.includes(activePossessionView)) activePossessionView = "player";
  possessionsTabs.replaceChildren();
  possessionsTabs.hidden = views.length < 2;
  for (const view of views) {
    const control = document.createElement("button");
    control.type = "button";
    control.className = "possession-tab";
    control.textContent = possessionViewLabel(view, view === "party" ? partyMembers.length : 0);
    const selected = view === activePossessionView;
    control.dataset.active = String(selected);
    control.setAttribute("aria-pressed", String(selected));
    control.addEventListener("click", () => {
      if (activePossessionView === view) return;
      activePossessionView = view;
      if (loadedPossessions) renderPossessions(loadedPossessions);
    });
    possessionsTabs.append(control);
  }
}

function renderPlayerQuickbar(data = {}) {
  if (!playerQuickbarList) return;
  const items = [...(data.equipped ?? []), ...(data.carried ?? [])]
    .filter((item) => item?.name && item.holder === "player")
    .filter((item, index, all) => all.findIndex((candidate) => candidate.id === item.id) === index)
    .slice(0, 6);
  playerQuickbarList.replaceChildren();
  if (!items.length) {
    const empty = document.createElement("span");
    empty.className = "quickbar-empty";
    empty.textContent = interfaceLanguage === "zh" ? "还没有可快速引用的随身物品" : "No carried items to reference yet";
    playerQuickbarList.append(empty);
    return;
  }
  for (const item of items) {
    const control = document.createElement("button");
    control.type = "button";
    control.className = "quickbar-item";
    control.title = interfaceLanguage === "zh" ? `将“${item.name}”写入行动` : `Use ${item.name} in your action`;
    control.textContent = item.name;
    control.addEventListener("click", () => insertSceneReference(item.name));
    playerQuickbarList.append(control);
  }
}

function renderPartyPossessions(partyMembers, partyItems) {
  for (const person of partyMembers) {
    const memberItems = partyItems.filter((item) => item.holder === person.id);
    const member = document.createElement("section");
    member.className = "party-inventory-member";
    member.dataset.partyMember = person.id;
    const heading = document.createElement("header");
    const title = document.createElement("h3");
    title.textContent = person.name;
    const role = document.createElement("span");
    role.textContent = person.role || (interfaceLanguage === "zh" ? "同行者" : "Party member");
    heading.append(title, role);
    member.append(heading);
    const equipped = memberItems.filter((item) => item.status === "equipped");
    const carried = memberItems.filter((item) => ["carried", "concealed"].includes(item.status));
    const stored = memberItems.filter((item) => item.status === "stored");
    const sections = [["Equipped", equipped], ["Carried", carried], ["Stored", stored]];
    let memberHasItems = false;
    for (const [titleLabel, items] of sections) {
      if (!items.length) continue;
      memberHasItems = true;
      appendPossessionSection(member, titleLabel, items);
    }
    if (!memberHasItems) {
      const empty = document.createElement("p");
      empty.className = "save-help";
      empty.textContent = interfaceLanguage === "zh" ? "尚未记录持有物。" : "No possessions recorded.";
      member.append(empty);
    }
    possessionsList.append(member);
  }
  return partyMembers.length > 0;
}

function focusPartyMemberGear(personId) {
  activePossessionView = "party";
  showJournalSection("backpack");
  if (loadedPossessions) renderPossessions(loadedPossessions);
  requestAnimationFrame(() => document.querySelector(`[data-party-member="${CSS.escape(personId)}"]`)
    ?.scrollIntoView({ behavior: "smooth", block: "start" }));
}

function renderPossessions(data) {
  loadedPossessions = data;
  renderPlayerQuickbar(data);
  possessionsList.replaceChildren();
  const partyMembers = (loadedCast?.party ?? []).filter((person) => person.status === "party");
  const partyIds = new Set(partyMembers.map((person) => person.id));
  const elsewhere = data.elsewhere ?? [];
  const partyItems = elsewhere.filter((item) => partyIds.has(item.holder));
  const otherItems = elsewhere.filter((item) => !partyIds.has(item.holder));
  renderPossessionTabs(partyMembers, otherItems);

  let hasItems = false;
  if (activePossessionView === "party") {
    hasItems = renderPartyPossessions(partyMembers, partyItems);
  } else if (activePossessionView === "other") {
    hasItems = appendPossessionSection(possessionsList, interfaceLanguage === "zh" ? "其他已记录物品" : "Other recorded items", otherItems);
  } else {
    const groups = [["Equipped", data.equipped ?? []], ["Important", data.important ?? []], ["Carried", data.carried ?? []]];
    for (const [title, items] of groups) hasItems = appendPossessionSection(possessionsList, title, items) || hasItems;
  }
  if (!hasItems) {
    const empty = document.createElement("p");
    empty.className = "save-help";
    empty.textContent = activePossessionView === "party"
      ? (interfaceLanguage === "zh" ? "小队成员尚未记录装备或持有物。" : "No party equipment or possessions are recorded yet.")
      : (interfaceLanguage === "zh" ? "尚无已记录物品。" : "Nothing notable is recorded yet.");
    possessionsList.append(empty);
  }
}

async function loadPossessions() {
  if (!activeWorldId) return;
  try {
    const [response, resourceResponse] = await Promise.all([fetch("/api/possessions"), fetch("/api/resources")]);
    const [data, resources] = await Promise.all([response.json(), resourceResponse.json()]);
    if (!response.ok) throw new Error(data.error ?? "Could not read possessions.");
    if (!resourceResponse.ok) throw new Error(resources.error ?? "Could not read resources.");
    renderPossessions(data);
    renderResources(resources);
  } catch (error) {
    possessionsList.replaceChildren();
    const failed = document.createElement("p");
    failed.className = "save-help";
    failed.textContent = error instanceof Error ? error.message : "Could not read possessions.";
    possessionsList.append(failed);
  }
}

function castPayload() {
  return {
    id: castId.value.trim(), name: castName.value.trim(), status: castStatus.value, tier: castTier.value,
    role: castRole.value.trim(), relationship: castRelationship.value.trim(), location: castLocation.value.trim(),
    activity: castActivity.value.trim(), anchor: castAnchor.value.trim(), pinned: castPinned.checked,
    description: castDescription.input.value.trim(), voice: castVoice.input.value.trim(),
    objective: castObjective.input.value.trim(), availability: castAvailability.input.value.trim(),
    next_move: castNextMove.input.value.trim()
  };
}

function resetCastForm() {
  castForm.reset();
  castId.value = "";
  castStatus.value = "known";
  castTier.value = "recurring";
  castPinned.checked = false;
  for (const field of [castDescription, castVoice, castObjective, castAvailability, castNextMove]) field.input.value = "";
}

function setCastForm(person) {
  castId.value = person.id ?? "";
  castName.value = person.name ?? "";
  castStatus.value = person.status ?? "known";
  castTier.value = person.tier ?? "recurring";
  castRole.value = person.role ?? "";
  castRelationship.value = person.relationship ?? "";
  castLocation.value = person.location ?? "";
  castActivity.value = person.activity ?? "";
  castAnchor.value = person.anchor ?? "";
  castDescription.input.value = person.description ?? "";
  castVoice.input.value = person.voice ?? "";
  castObjective.input.value = person.objective ?? "";
  castAvailability.input.value = person.availability ?? "";
  castNextMove.input.value = person.next_move ?? "";
  castPinned.checked = Boolean(person.pinned);
  document.querySelector("#cast-drawer").open = true;
  castEditor.open = true;
  castForm.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function castGroupTitle(group) {
  return localized(({ party: "Party", core: "Core people", known: "Known people", away: "Away", archived: "Archive" })[group] ?? group);
}

function renderCast(data) {
  loadedCast = data;
  rebuildHolderOptions();
  if (loadedPossessions) renderPossessions(loadedPossessions);
  const partyMembers = Array.isArray(data.party) ? data.party : [];
  partyOverviewCopy.textContent = partyMembers.length
    ? (interfaceLanguage === "zh" ? `${partyMembers.length} 人同行。点击成员可定位档案，或直接查看其装备。` : `${partyMembers.length} travelling with you. Select a member to reach their profile or gear.`)
    : (interfaceLanguage === "zh" ? "目前没有成员同行；重要人物仍会保留在下方人物档案中。" : "No one is travelling with you yet; important people remain in the cast below.");
  partyRoster.replaceChildren();
  for (const person of partyMembers) {
    const rosterCard = document.createElement("button");
    rosterCard.type = "button";
    rosterCard.className = "party-roster-card";
    rosterCard.title = interfaceLanguage === "zh" ? `查看 ${person.name}` : `View ${person.name}`;
    const name = document.createElement("strong");
    name.textContent = person.name;
    const role = document.createElement("small");
    role.textContent = person.role || (interfaceLanguage === "zh" ? "同行者" : "Party member");
    rosterCard.append(name, role);
    rosterCard.addEventListener("click", () => {
      const target = document.querySelector(`.person-card[data-person-id="${CSS.escape(person.id)}"]`);
      target?.scrollIntoView({ behavior: "smooth", block: "center" });
      target?.querySelector(".record-card-more")?.setAttribute("open", "");
    });
    partyRoster.append(rosterCard);
  }
  castList.replaceChildren();
  const groups = ["party", "core", "known", "away", "archived"];
  let any = false;
  for (const group of groups) {
    const people = data[group] ?? [];
    if (!people.length) continue;
    any = true;
    const section = document.createElement("section");
    section.className = "cast-section";
    const heading = document.createElement("h3");
    heading.textContent = castGroupTitle(group);
    const list = document.createElement("ul");
    for (const person of people) {
      const row = document.createElement("li");
      row.className = "record-card person-card";
      row.dataset.personId = person.id;
      const identity = document.createElement("div");
      identity.className = "record-card-heading";
      const title = document.createElement("div");
      const name = document.createElement("strong");
      name.textContent = person.name;
      const meta = document.createElement("small");
      meta.textContent = person.role || (interfaceLanguage === "zh" ? "个人身份未记录" : "Role unrecorded");
      const badge = document.createElement("span");
      badge.className = "record-card-badge";
      badge.textContent = person.status === "deceased" ? localized("Dead") : castGroupTitle(person.status);
      title.append(name, meta);
      identity.append(title, badge);
      row.append(identity);
      const identityFacts = [person.ancestry, person.gender, person.age_stage].filter(Boolean).join(" · ");
      const height = person.height_cm !== null && person.height_cm !== undefined && Number.isFinite(Number(person.height_cm))
        ? `${person.height_cm} cm`
        : "";
      const weight = person.weight_kg !== null && person.weight_kg !== undefined && Number.isFinite(Number(person.weight_kg))
        ? `${person.weight_kg} kg`
        : "";
      const profileFacts = [
        [interfaceLanguage === "zh" ? "族裔 / 性别 / 年龄" : "Ancestry / gender / age", identityFacts],
        [interfaceLanguage === "zh" ? "身高" : "Height", height],
        [interfaceLanguage === "zh" ? "体重" : "Weight", weight]
      ].filter(([, value]) => value);
      if (profileFacts.length) {
        const facts = document.createElement("dl");
        facts.className = "person-profile-facts";
        for (const [label, value] of profileFacts) {
          const fact = document.createElement("div");
          const term = document.createElement("dt");
          term.textContent = label;
          const description = document.createElement("dd");
          description.textContent = value;
          fact.append(term, description);
          facts.append(fact);
        }
        row.append(facts);
      }
      for (const [label, value] of [
        [interfaceLanguage === "zh" ? "外貌" : "Appearance", person.appearance || person.description],
        [interfaceLanguage === "zh" ? "性格" : "Personality", person.personality]
      ]) {
        if (!value) continue;
        const profile = document.createElement("p");
        profile.className = "person-profile-summary";
        const labelNode = document.createElement("strong");
        labelNode.textContent = label;
        const valueNode = document.createElement("span");
        valueNode.textContent = value;
        profile.append(labelNode, valueNode);
        row.append(profile);
      }
      const extra = [
        [interfaceLanguage === "zh" ? "个人经历" : "Background", person.background],
        [interfaceLanguage === "zh" ? "说话方式" : "Voice", person.voice]
      ].filter(([, value]) => value);
      const personAttributes = person.attributes && typeof person.attributes === "object" ? person.attributes : {};
      const personAbilities = Array.isArray(person.abilities) ? person.abilities : [];
      const personSpecialties = Array.isArray(person.specialties) ? person.specialties : [];
      if (extra.length || personAbilities.length || personSpecialties.length || Object.keys(personAttributes).length) {
        const more = document.createElement("details");
        more.className = "record-card-more";
        const summary = document.createElement("summary");
        summary.textContent = interfaceLanguage === "zh" ? "人物档案" : "Person details";
        more.append(summary);
        for (const [label, value] of extra) {
          const detail = document.createElement("p");
          detail.textContent = `${label} · ${value}`;
          more.append(detail);
        }
        if (Object.keys(personAttributes).length) {
          const mechanicsHeading = document.createElement("h4");
          mechanicsHeading.textContent = interfaceLanguage === "zh" ? "七项属性" : "Seven attributes";
          const grid = document.createElement("div");
          grid.className = "npc-attribute-grid";
          const labels = {
            physique: "Physique", agility: "Agility", perception: "Perception", intellect: "Intellect",
            will: "Will", charisma: "Charisma", mystic_power: "Mystic power"
          };
          for (const key of attributeKeys) {
            if (!Number.isFinite(Number(personAttributes[key]))) continue;
            const item = document.createElement("div");
            const label = document.createElement("span");
            label.textContent = localized(labels[key]);
            const value = document.createElement("strong");
            value.textContent = String(personAttributes[key]);
            item.append(label, value);
            grid.append(item);
          }
          more.append(mechanicsHeading, grid);
        }
        if (personSpecialties.length) {
          const specialtiesHeading = document.createElement("h4");
          specialtiesHeading.textContent = interfaceLanguage === "zh" ? "专业" : "Specialties";
          const specialties = document.createElement("p");
          specialties.className = "npc-specialties";
          specialties.textContent = personSpecialties.join(" · ");
          more.append(specialtiesHeading, specialties);
        }
        if (personAbilities.length) {
          const abilitiesHeading = document.createElement("h4");
          abilitiesHeading.textContent = interfaceLanguage === "zh" ? "能力、技法与法术" : "Abilities, techniques & spells";
          const abilityRecords = document.createElement("div");
          abilityRecords.className = "npc-ability-list";
          for (const ability of personAbilities) {
            const abilityRecord = document.createElement("article");
            abilityRecord.className = "npc-ability-record";
            const abilityTitle = document.createElement("div");
            const name = document.createElement("strong");
            name.textContent = ability.name;
            const mastery = document.createElement("span");
            mastery.textContent = ability.mastery_label;
            abilityTitle.append(name, mastery);
            const effect = document.createElement("p");
            effect.textContent = ability.known_effect;
            const limits = document.createElement("small");
            limits.textContent = `${interfaceLanguage === "zh" ? "边界" : "Limits"}：${ability.limits}`;
            abilityRecord.append(abilityTitle, effect, limits);
            abilityRecords.append(abilityRecord);
          }
          more.append(abilitiesHeading, abilityRecords);
        }
        row.append(more);
      }
      const quickActions = document.createElement("div");
      quickActions.className = "record-quick-actions person-quick-actions";
      quickActions.append(actionButton(
        interfaceLanguage === "zh" ? "查看档案" : "View profile",
        () => {
          const details = row.querySelector(".record-card-more");
          if (details) details.open = true;
          row.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      ));
      if (person.status === "party") {
        quickActions.append(actionButton(interfaceLanguage === "zh" ? "查看装备" : "View gear", () => focusPartyMemberGear(person.id)));
      }
      if (person.status !== "deceased" && person.status !== "archived") {
        const nextStatus = person.status === "party" ? (person.tier === "core" ? "core" : "known") : "party";
        const nextLabel = person.status === "party"
          ? (interfaceLanguage === "zh" ? "离开小队" : "Leave party")
          : (interfaceLanguage === "zh" ? "加入小队" : "Join party");
        quickActions.append(actionButton(nextLabel, async (control) => {
          control.disabled = true;
          try {
            await saveCast({
              id: person.id,
              name: person.name,
              status: nextStatus,
              tier: person.tier,
              pinned: nextStatus === "party" || person.pinned,
              role: person.role,
              description: person.description || person.appearance,
              voice: person.voice,
              relationship: person.relationship,
              location: person.location,
              activity: person.activity,
              objective: person.objective,
              availability: person.availability,
              next_move: person.next_move,
              anchor: person.anchor
            });
            journalStatus.textContent = nextStatus === "party"
              ? (interfaceLanguage === "zh" ? `${person.name} 已加入小队。` : `${person.name} joined the party.`)
              : (interfaceLanguage === "zh" ? `${person.name} 已离开小队，但仍保留在人物档案中。` : `${person.name} left the party and remains in the cast.`);
          } catch (error) {
            journalStatus.textContent = error instanceof Error ? error.message : (interfaceLanguage === "zh" ? "小队状态保存失败。" : "Could not update the party.");
            control.disabled = false;
          }
        }));
      }
      row.append(quickActions);
      list.append(row);
    }
    section.append(heading, list);
    castList.append(section);
  }
  if (!any) {
    const empty = document.createElement("p");
    empty.className = "save-help";
    empty.textContent = localized("No important people are recorded yet. Named people who become significant are saved here with the campaign.");
    castList.append(empty);
  }
}

async function loadCast() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/cast");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? localized("Could not read cast."));
    loadedCast = data;
    renderCast(data);
  } catch (error) {
    castList.replaceChildren();
    const failed = document.createElement("p");
    failed.className = "save-help";
    failed.textContent = error instanceof Error ? error.message : localized("Could not read cast.");
    castList.append(failed);
  }
}

async function saveCast(person) {
  const data = await saveRequest("/api/cast", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(person) });
  loadedCast = data.cast;
  renderCast(data.cast);
  return data;
}

function castFieldLabel(field) {
  const labels = {
    name: ["name", "姓名"], role: ["role", "身份"], status: ["story status", "故事状态"],
    tier: ["continuity tier", "延续层级"], relationship: ["relationship", "关系"],
    location: ["location", "位置"], activity: ["activity", "当前活动"], objective: ["objective", "目标"],
    availability: ["availability", "可联络状态"], next_move: ["next move", "下一步意图"],
    anchor: ["relationship anchor", "关系锚点"], pinned: ["active continuity", "核心记忆"], memory: ["new memory", "新记忆"]
  };
  const pair = labels[field] ?? [field, field];
  return pair[interfaceLanguage === "zh" ? 1 : 0];
}

function displayCastValue(value) {
  if (typeof value === "boolean") return value ? (interfaceLanguage === "zh" ? "是" : "yes") : (interfaceLanguage === "zh" ? "否" : "no");
  return String(value ?? "—");
}

function renderCastChanges(changes) {
  lastCastChanges = Array.isArray(changes) ? changes : [];
  castChangeList.replaceChildren();
  castChangeNotice.hidden = !lastCastChanges.length;
  for (const change of lastCastChanges) {
    const line = document.createElement("p");
    if (change.kind === "created") {
      const detail = change.relationship || change.role || change.status;
      line.textContent = interfaceLanguage === "zh"
        ? `新人物已记录：${change.name}${detail ? ` · ${detail}` : ""}`
        : `New person recorded: ${change.name}${detail ? ` · ${detail}` : ""}`;
    } else {
      const fields = (change.fields ?? []).map((item) => {
        const label = castFieldLabel(item.field);
        if (item.field === "memory") return `${label}：${displayCastValue(item.after)}`;
        return `${label}：${displayCastValue(item.before)} → ${displayCastValue(item.after)}`;
      });
      line.textContent = `${change.name} · ${fields.join(interfaceLanguage === "zh" ? "；" : "; ")}`;
    }
    castChangeList.append(line);
  }
}

function renderLore(entries) {
  loreList.replaceChildren();
  if (!entries.length) {
    const empty = document.createElement("li");
    empty.textContent = "No worldbook entries yet.";
    loreList.append(empty);
    return;
  }
  for (const entry of entries) {
    const row = document.createElement("li");
    const label = document.createElement("strong");
    label.textContent = entry.title;
    const details = document.createElement("small");
    const trigger = entry.constant ? "always active" : (entry.keys.length ? `keywords: ${entry.keys.join(", ")}` : "no keywords");
    details.textContent = `${trigger} · priority ${entry.priority}`;
    const body = document.createElement("span");
    body.className = "lore-body";
    body.textContent = entry.content;
    row.append(label, details, body);
    row.append(actionButton("Remove", async () => {
      if (!confirm(`Remove lore entry “${entry.title}”?`)) return;
      const data = await saveRequest(`/api/lore/${encodeURIComponent(entry.id)}`, { method: "DELETE" });
      renderLore(data.entries);
    }, true));
    loreList.append(row);
  }
}

async function loadLore() {
  if (!activeWorldId) return;
  try {
    const response = await fetch("/api/lore");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not read the worldbook.");
    renderLore(data.entries);
  } catch (error) {
    loreList.replaceChildren();
    const failed = document.createElement("li");
    failed.textContent = error instanceof Error ? error.message : "Could not read the worldbook.";
    loreList.append(failed);
  }
}

async function loadModels() {
  try {
    const response = await fetch("/api/models");
    const data = await response.json();
    if (!response.ok || !data.models?.length) throw new Error(data.error ?? "No models are available.");
    const remembered = localStorage.getItem("codex-rpg-model");
    const qualityDefault = data.models.find((model) => model.id === "gpt-5.6-sol");
    const selectedRemembered = remembered === "gpt-5.6-terra" && qualityDefault ? qualityDefault.id : remembered;
    if (selectedRemembered && selectedRemembered !== remembered) localStorage.setItem("codex-rpg-model", selectedRemembered);
    outputDensity.value = localStorage.getItem("codex-rpg-output-density") ?? "standard";
    modelSelect.replaceChildren();
    for (const model of data.models) {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = `${model.name}${model.isDefault ? " (default)" : ""}`;
      option.selected = model.id === selectedRemembered || (!selectedRemembered && model.isDefault);
      modelSelect.append(option);
    }
    if (!modelSelect.value) modelSelect.selectedIndex = 0;
    modelSelect.dataset.pinned = String(Boolean(data.pinned));
    modelSelect.dataset.loaded = "true";
    modelSelect.disabled = Boolean(data.pinned);
    if (!activeWorldId) {
      status.textContent = "Model list loaded locally.";
    } else {
      status.textContent = localized(data.pinned ? "The narrator model is fixed by the local launch setting." : "Ready to begin.");
      button.disabled = false;
      field.disabled = false;
      speechField.disabled = false;
    }
  } catch (error) {
    status.textContent = error instanceof Error ? `Could not read Codex models: ${error.message}` : "Could not read Codex models.";
    // The preferred model still resolves on the next actual game turn, so a
    // failed optional model picker never blocks play.
    if (activeWorldId) {
      button.disabled = false;
      field.disabled = false;
      speechField.disabled = false;
    }
  }
}

modelSelect.addEventListener("change", () => localStorage.setItem("codex-rpg-model", modelSelect.value));
for (const control of [outputDensity, narratorPacing, narratorProse, narratorSceneEnd, narratorFocus, narratorDialogue, narratorAgency, narratorNpcInitiative, narratorMaturity]) {
  control.addEventListener("change", () => {
    narratorProfile.value = "custom";
    saveNarratorSettings();
  });
}
narratorProfile.addEventListener("change", () => {
  const profile = narratorProfiles[narratorProfile.value];
  if (profile) writeNarratorSettings({ ...profile, directorNote: narratorDirectorNote.value });
  saveNarratorSettings();
});
narratorDirectorNote.addEventListener("input", updateDirectorCount);
narratorDirectorNote.addEventListener("change", () => {
  narratorProfile.value = "custom";
  saveNarratorSettings();
});
restoreNarratorDefaultsButton.addEventListener("click", () => {
  writeNarratorSettings(narratorDefaults);
  saveNarratorSettings();
  narratorSettingsStatus.textContent = interfaceLanguage === "zh" ? "已在本机恢复推荐默认配置。" : "Recommended defaults restored locally.";
});
languageToggle.addEventListener("click", () => {
  interfaceLanguage = interfaceLanguage === "en" ? "zh" : "en";
  localStorage.setItem("codex-rpg-language", interfaceLanguage);
  applyLanguage();
});
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const action = composeTurnInput(field.value, speechField.value);
  if (!action) {
    turnInputHelp.textContent = interfaceLanguage === "zh" ? "请至少填写行为或说话。" : "Write an action or speech before sending.";
    turnInputHelp.classList.add("input-warning");
    field.focus();
    return;
  }
  turnInputHelp.textContent = localized("Write an action, speech, or both. Neither needs a preset category.");
  turnInputHelp.classList.remove("input-warning");
  story.querySelectorAll(".turn-error").forEach((entry) => entry.remove());
  actionClarification.hidden = true;
  const pendingAction = append("action", action);
  const pendingTurn = appendTurnPending();
  field.disabled = true;
  speechField.disabled = true;
  button.disabled = true;
  button.setAttribute("aria-busy", "true");
  const originalButtonLabel = button.textContent;
  button.textContent = interfaceLanguage === "zh" ? "生成中…" : "Generating…";
  modelSelect.disabled = true;
  try {
    const response = await localRequest("/api/turn", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ action, model: modelSelect.value, outputDensity: outputDensity.value, narratorSettings: narratorSettingsPayload() })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "The turn did not complete.");
    pendingTurn.stop();
    if (data.clarification) {
      pendingAction.remove();
      actionClarification.textContent = data.clarification;
      actionClarification.hidden = false;
      status.textContent = data.token_usage?.available
        ? (interfaceLanguage === "zh" ? `澄清问题消耗 ${Number(data.token_usage.total).toLocaleString()} Token，未保存为剧情回合。` : `Clarification used ${Number(data.token_usage.total).toLocaleString()} tokens; no story turn was saved.`)
        : (interfaceLanguage === "zh" ? "需要澄清；本次用量未提供，未保存剧情回合。" : "Clarification needed; token usage unavailable, no story turn saved.");
      return;
    }
    append("narration", data.narration);
    field.value = "";
    speechField.value = "";
    if (!gameMap.hidden) void loadMap();
    const usedSceneMode = writingReferenceById[data.scene_mode];
    if (usedSceneMode) {
      recentSceneModes = [...recentSceneModes.filter((id) => id !== usedSceneMode.id), usedSceneMode.id].slice(-2);
    }
    const manualSceneMode = sceneMode !== "auto";
    if (manualSceneMode) sceneMode = "auto";
    renderWritingReferenceLibrary();
    saveNarratorSettings();
    status.textContent = usedSceneMode
      ? `Turn saved locally · ${usedSceneMode.label}${manualSceneMode ? " · automatic matching restored" : ""}.`
      : "Turn saved to your local chronicle.";
    renderPossessionSuggestions(data.possession_suggestions);
    renderCastChanges(data.cast_changes);
    void loadSaveState();
    void loadPossessions();
    void loadCast();
    void refreshActiveWorldOverview();
  } catch (error) {
    pendingTurn.stop();
    pendingAction.remove();
    const failure = append("error", error instanceof Error ? error.message : "The turn encountered an error.");
    failure.classList.add("turn-error");
    status.textContent = interfaceLanguage === "zh"
      ? "本轮没有写入存档，输入内容已保留，可以直接重新发送。"
      : "This turn was not saved. Your input is still here and can be sent again.";
  } finally {
    button.textContent = originalButtonLabel;
    button.removeAttribute("aria-busy");
    field.disabled = false;
    speechField.disabled = false;
    button.disabled = false;
    modelSelect.disabled = modelSelect.dataset.loaded !== "true" || modelSelect.dataset.pinned === "true";
    field.focus();
  }
});

possessionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const item = possessionPayload();
  if (!item.name) return;
  if (!item.base_type_id) {
    await suggestPossessionType();
    status.textContent = possessionType.value
      ? (interfaceLanguage === "zh" ? "请核对建议的基础类别，再保存一次。" : "Review the suggested base category, then save again.")
      : (interfaceLanguage === "zh" ? "无法确定基础类别，请从列表选择后保存。" : "Choose a base category before saving.");
    return;
  }
  const submit = possessionForm.querySelector("button[type=submit]");
  submit.disabled = true;
  try {
    await savePossession(item);
    pendingPossessionSuggestions = pendingPossessionSuggestions.filter((suggestion) => suggestion.id ? suggestion.id !== item.id : suggestion.name !== item.name);
    renderPossessionSuggestions(pendingPossessionSuggestions);
    resetPossessionForm();
    status.textContent = "Possession saved locally.";
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "Could not save possession.";
  } finally {
    submit.disabled = false;
  }
});

possessionResetButton.addEventListener("click", resetPossessionForm);

castForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const person = castPayload();
  if (!person.name) return;
  const submit = castForm.querySelector("button[type=submit]");
  submit.disabled = true;
  try {
    await saveCast(person);
    resetCastForm();
    status.textContent = localized("Person saved in this local timeline.");
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : localized("Could not save person.");
  } finally {
    submit.disabled = false;
  }
});

castResetButton.addEventListener("click", resetCastForm);

chapterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const start = Number(chapterStart.value);
  const end = Number(chapterEnd.value);
  if (!Number.isInteger(start) || !Number.isInteger(end) || start < 1 || end < start) {
    chapterStatus.textContent = interfaceLanguage === "zh" ? "请选择有效的起止回合。" : "Choose a valid start and end turn.";
    return;
  }
  if (end - start + 1 > 50) {
    chapterStatus.textContent = interfaceLanguage === "zh" ? "一个章节最多覆盖 50 个回合。" : "One chapter may cover at most 50 turns.";
    return;
  }
  const submit = chapterForm.querySelector("button[type=submit]");
  submit.disabled = true;
  chapterStatus.textContent = interfaceLanguage === "zh" ? "Codex 正在根据原始回合生成可审核草稿…" : "Codex is drafting from the exact source turns…";
  try {
    const data = await saveRequest("/api/chapters/draft", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ start_turn: start, end_turn: end, model: modelSelect.value })
    });
    renderChapters(data);
    chapterStatus.textContent = interfaceLanguage === "zh"
      ? "草稿已保存。请核对原文、编辑并确认。"
      : "Draft saved. Review its source, edit it, then approve.";
  } catch (error) {
    chapterStatus.textContent = error instanceof Error ? error.message : "Could not generate chapter draft.";
  } finally {
    submit.disabled = false;
  }
});

checkpointForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = checkpointName.value.trim();
  if (!name) return;
  try {
    renderSaveState(await saveRequest("/api/checkpoints", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name })
    }));
    checkpointName.value = "";
  } catch (error) {
    timelineStatus.textContent = error instanceof Error ? error.message : "Could not create this save.";
  }
});

worldForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = worldTitle.value.trim();
  const player = worldPlayer.value.trim();
  const location = creatorFieldValue(worldLocation, worldLocationCustom);
  const concept = creatorFieldValue(worldConcept, worldConceptCustom) || "adventurer";
  if (!title || !player || !location) return;
  try {
    const response = await saveRequest("/api/worlds", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        preset_id: selectedCharacterPresetId || null,
        title,
        player,
        concept,
        location,
        background: worldBackground.value.trim(),
        character: characterDraft(),
        signature_item: worldSignatureItem.value.trim() ? {
          name: worldSignatureItem.value.trim(),
          description: worldSignatureDetail.value.trim(),
          category: "important", status: "carried", importance: 8, quantity: 1
        } : null
      })
    });
    worldForm.reset();
    selectedCharacterPresetId = "";
    worldAncestry.value = "";
    syncCreatorChoices();
    updateCharacterPreview();
    renderWorlds(response);
    showGame(response.worlds.find((world) => world.id === response.active_campaign));
    void loadSaveState();
    void loadPossessions();
    void loadCast();
    void loadLore();
    void loadUniverseLore();
    void loadTimeline();
  } catch (error) {
    worldStatus.textContent = error instanceof Error ? error.message : "Could not create this world.";
  }
});

loreForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = loreTitle.value.trim();
  const content = loreContent.value.trim();
  if (!title || !content) return;
  try {
    const data = await saveRequest("/api/lore", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        title,
        content,
        keys: loreKeys.value,
        constant: loreConstant.checked,
        priority: Number(lorePriority.value)
      })
    });
    loreForm.reset();
    lorePriority.value = "50";
    renderLore(data.entries);
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "Could not add lore.";
  }
});

restartButton.addEventListener("click", async () => {
  if (!confirm("Restart this campaign? All turns, timelines, and named saves will be permanently deleted. The initial player and setting will remain.")) return;
  try {
    renderSaveState(await saveRequest("/api/restart", { method: "POST" }));
    void loadTimeline();
    void loadPossessions();
    void loadCast();
    status.textContent = "Campaign restarted and local storage reclaimed.";
  } catch (error) {
    timelineStatus.textContent = error instanceof Error ? error.message : "Could not restart this campaign.";
  }
});

reviewCastChangesButton.addEventListener("click", () => {
  if (gameJournal.hidden) toggleJournal();
  showJournalSection("party");
  document.querySelector("#cast-drawer").open = true;
});

backupDatabaseButton.addEventListener("click", async () => {
  backupDatabaseButton.disabled = true;
  dataProtectionStatus.textContent = interfaceLanguage === "zh" ? "正在创建一致性备份…" : "Creating a consistent backup…";
  try {
    const data = await saveRequest("/api/database/backup", { method: "POST" });
    dataProtectionStatus.textContent = interfaceLanguage === "zh"
      ? `备份已保存：${data.backup.filename}`
      : `Backup saved: ${data.backup.filename}`;
  } catch (error) {
    dataProtectionStatus.textContent = error instanceof Error ? error.message : "Could not create a backup.";
  } finally {
    backupDatabaseButton.disabled = false;
  }
});

exportDatabaseButton.addEventListener("click", async () => {
  exportDatabaseButton.disabled = true;
  dataProtectionStatus.textContent = interfaceLanguage === "zh" ? "正在准备便携副本…" : "Preparing a portable copy…";
  try {
    const response = await fetch("/api/database/export");
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error ?? "Could not export the database.");
    }
    const disposition = response.headers.get("content-disposition") ?? "";
    const filename = disposition.match(/filename="([^"]+)"/)?.[1] ?? "secret-fire.sqlite3";
    const url = URL.createObjectURL(await response.blob());
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.append(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    dataProtectionStatus.textContent = interfaceLanguage === "zh" ? `已导出：${filename}` : `Exported: ${filename}`;
  } catch (error) {
    dataProtectionStatus.textContent = error instanceof Error ? error.message : "Could not export the database.";
  } finally {
    exportDatabaseButton.disabled = false;
  }
});

importDatabaseInput.addEventListener("change", async () => {
  const file = importDatabaseInput.files?.[0];
  if (!file) return;
  const prompt = interfaceLanguage === "zh"
    ? "导入会替换当前的全部世界与存档。系统会先自动备份当前数据库。继续吗？"
    : "Importing replaces every current world and save. The current database will be backed up automatically first. Continue?";
  if (!confirm(prompt)) {
    importDatabaseInput.value = "";
    return;
  }
  importDatabaseInput.disabled = true;
  dataProtectionStatus.textContent = interfaceLanguage === "zh" ? "正在校验、迁移并恢复存档…" : "Checking, migrating, and restoring the save…";
  try {
    const response = await localRequest("/api/database/import", {
      method: "POST",
      headers: { "content-type": "application/vnd.sqlite3" },
      body: file
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error ?? "Could not import the database.");
    renderWorlds(data);
    renderCastChanges([]);
    showHome();
    dataProtectionStatus.textContent = interfaceLanguage === "zh"
      ? `恢复完成：${data.restored.campaigns} 个世界，数据库版本 ${data.restored.schema_version}。`
      : `Restore complete: ${data.restored.campaigns} world(s), database schema ${data.restored.schema_version}.`;
  } catch (error) {
    dataProtectionStatus.textContent = error instanceof Error ? error.message : "Could not import the database.";
  } finally {
    importDatabaseInput.disabled = false;
    importDatabaseInput.value = "";
  }
});

changeWorldButton.addEventListener("click", () => showWorlds(false));
openMapButton.addEventListener("click", toggleMap);
closeMapButton.addEventListener("click", closeMap);
openJournalButton.addEventListener("click", toggleJournal);
openCharacterCardButton.addEventListener("click", () => openInformationCard("character"));
openPartyCardButton.addEventListener("click", () => openInformationCard("party"));
openPlayerBackpackButton.addEventListener("click", () => {
  activePossessionView = "player";
  openInformationCard("backpack");
});
openPartyBackpackButton.addEventListener("click", () => {
  activePossessionView = "party";
  openInformationCard("backpack");
});
closeJournalButton.addEventListener("click", closeJournal);
openManagementButton.addEventListener("click", showManagement);
backToGameButton.addEventListener("click", () => {
  showGame(activeWorldSnapshot);
  void refreshActiveWorldOverview();
  void loadTimeline();
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !gameMap.hidden) {
    closeMap();
    openMapButton.focus();
  }
  if (event.key === "Escape" && !gameJournal.hidden) {
    closeJournal();
    openJournalButton.focus();
  }
});
navHomeButton.addEventListener("click", showHome);
navWorldsButton.addEventListener("click", () => showWorlds(false));
navUniverseButton.addEventListener("click", showUniverse);
navSettingsButton.addEventListener("click", showSettings);
openWorldsButton.addEventListener("click", () => showWorlds(false));
openUniverseButton.addEventListener("click", showUniverse);
openSettingsButton.addEventListener("click", showSettings);
newWorldButton.addEventListener("click", () => showWorlds(true));
cancelCreateWorldButton.addEventListener("click", () => showWorlds(false));

async function initialize() {
  loadNarratorSettings();
  try {
    await loadCharacterPresets();
  } catch (error) {
    characterPresets = [];
    worldStatus.textContent = error instanceof Error ? error.message : "Could not load starting characters.";
  }
  try {
    await loadItemTypes();
  } catch (error) {
    possessionTypeHint.textContent = error instanceof Error ? error.message : "Could not load item types.";
  }
  await loadModels();
  await loadWorlds();
  if (activeWorldId) {
    void loadSaveState();
    void loadPossessions();
    void loadAbilities();
    void loadCast();
    void loadLore();
    void loadUniverseLore();
    void loadTimeline();
  }
}

applyLanguage();

if (location.protocol === "file:") {
  // A direct file preview has no server, no SQLite access, and no Codex
  // bridge. Keep it on a deliberate launch screen instead of letting menu
  // clicks land on an empty game or an unavailable encyclopedia.
  showHome();
  sourcePreview.hidden = false;
  status.textContent = "Source preview — start the local app to connect Codex and saves.";
  homeCurrentMeta.textContent = "Run npm run start in the project folder, then open the local address.";
  modelSelect.disabled = true;
  worldForm.querySelector("button[type=submit]").disabled = true;
  newWorldButton.disabled = true;
  field.disabled = true;
  speechField.disabled = true;
  button.disabled = true;
  for (const control of [navWorldsButton, navUniverseButton, navSettingsButton, openWorldsButton, openUniverseButton, openSettingsButton, continueWorldButton]) {
    control.disabled = true;
  }
} else {
  void initialize();
}
