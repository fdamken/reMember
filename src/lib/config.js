"use strict";

if (!window.reMember) {
    window.reMember = {};
}

class _Config {
    constructor(
        page_width,
        separator_clearance,
        margin_top,
        margin_right,
        margin_bottom,
        margin_left,
        vertical_separator_height,
        horizontal_separator_width,
        card_clearance,
        black_threshold,
        separator_threshold,
        require_top_horizontal_separator,
        require_bottom_horizontal_separator,
        switch_front_back,
        deck_id,
        deck_name,
        package_name,
        debug,
    ) {
        this.page_width = page_width;
        this.separator_clearance = separator_clearance;
        this.margin_top = margin_top;
        this.margin_right = margin_right;
        this.margin_bottom = margin_bottom;
        this.margin_left = margin_left;
        this.vertical_separator_height = vertical_separator_height;
        this.horizontal_separator_width = horizontal_separator_width;
        this.card_clearance = card_clearance;
        this.black_threshold = black_threshold;
        this.separator_threshold = separator_threshold;
        this.require_top_horizontal_separator = require_top_horizontal_separator;
        this.require_bottom_horizontal_separator = require_bottom_horizontal_separator
        this.switch_front_back = switch_front_back;
        this.deck_id = deck_id;
        this.deck_name = deck_name;
        this.package_name = package_name;
        this.debug = debug;
    }
}

window.reMember.Config = _Config;
