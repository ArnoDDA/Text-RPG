const rarityIds = new Set(["common", "rare", "exceptional", "legendary", "mythic"]);
const contextIds = new Set(["everyday", "specialist_access", "restricted_source", "historic_provenance", "mythic_provenance"]);

function knownMatch(item, knownItems) {
  const id = typeof item.id === "string" ? item.id.trim() : "";
  const name = typeof item.name === "string" ? item.name.trim() : "";
  return knownItems.find((known) => (id && known.id === id) || (name && known.name === name));
}

export function applyRarityAvailability(item, knownItems = []) {
  const requested = rarityIds.has(item.rarity) ? item.rarity : "common";
  const context = contextIds.has(item.rarity_context) ? item.rarity_context : "everyday";
  const basis = typeof item.rarity_basis === "string" ? item.rarity_basis.trim().slice(0, 500) : "";
  const known = knownMatch(item, knownItems);

  // A confirmed record is authoritative when the same item merely changes
  // hands or state. An unidentified record may still be identified later.
  if (known && known.rarity_known !== false && rarityIds.has(known.rarity)) {
    return {
      ...item,
      rarity: known.rarity,
      rarity_context: "existing_record",
      rarity_basis: basis,
      rarity_known: true
    };
  }

  let accepted = "common";
  let rarityKnown = requested === "common";
  if (requested === "rare") {
    if (basis && context !== "everyday") {
      accepted = "rare";
      rarityKnown = true;
    }
  } else if (requested === "exceptional") {
    if (basis && ["restricted_source", "historic_provenance", "mythic_provenance"].includes(context)) {
      accepted = "exceptional";
      rarityKnown = true;
    }
    else if (basis && context === "specialist_access") {
      accepted = "rare";
    }
  } else if (requested === "legendary") {
    if (basis && ["historic_provenance", "mythic_provenance"].includes(context)) {
      accepted = "legendary";
      rarityKnown = true;
    } else if (basis && context === "restricted_source") accepted = "exceptional";
    else if (basis && context === "specialist_access") accepted = "rare";
  } else if (requested === "mythic") {
    if (basis && context === "mythic_provenance") {
      accepted = "mythic";
      rarityKnown = true;
    } else if (basis && context === "historic_provenance") accepted = "legendary";
    else if (basis && context === "restricted_source") accepted = "exceptional";
    else if (basis && context === "specialist_access") accepted = "rare";
  }

  return {
    ...item,
    rarity: accepted,
    rarity_context: context,
    rarity_basis: basis,
    rarity_known: rarityKnown
  };
}
