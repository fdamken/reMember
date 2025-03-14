"use strict";

if (!window.reMember) {
    window.reMember = {};
}

const extract_card_boxes = function (config, image) {
    const separator_clearance = reMember.util.mm_to_pixels(config, image, config.separator_clearance);
    const vertical_separator_height = reMember.util.mm_to_pixels(
        config,
        image,
        config.vertical_separator_height,
    );
    const horizontal_separator_width = reMember.util.mm_to_pixels(
        config,
        image,
        config.horizontal_separator_width,
    );
    const margin_top = reMember.util.mm_to_pixels(config, image, config.margin_top);
    const margin_right = reMember.util.mm_to_pixels(config, image, config.margin_right);
    const margin_bottom = reMember.util.mm_to_pixels(config, image, config.margin_bottom);
    const margin_left = reMember.util.mm_to_pixels(config, image, config.margin_left);
    const horizontal_separator_box = new reMember.util.Rectangle(margin_left, margin_left + horizontal_separator_width, 0, image.height);
    const horizontal_separators = [];
    if (!config.require_top_horizontal_separator) {
        horizontal_separators.push(margin_top);
    }
    horizontal_separators.push(...reMember.separators.extract_from_box(config, image, horizontal_separator_box, false));
    if (!config.require_bottom_horizontal_separator) {
        horizontal_separators.push(image.height - margin_bottom);
    }
    const boxes = [];
    const vertical_separators_box = [];
    const vertical_separators_candidates = [];
    const vertical_separators = [];
    for (let i = 0; i < horizontal_separators.length - 1; i++) {
        const y = horizontal_separators[i];
        const y_next = horizontal_separators[i + 1];
        const vertical_separator_box = new reMember.util.Rectangle(
            0,
            image.width,
            y,
            y + vertical_separator_height,
        );
        vertical_separators_box.push(vertical_separator_box);
        const vertical_separator_candidates = reMember.separators.extract_from_box(
            config,
            image,
            vertical_separator_box,
            true,
        );
        vertical_separators_candidates.push(vertical_separator_candidates);
        const vertical_separator = vertical_separator_candidates[0];
        vertical_separators.push(vertical_separator);
        const left = new reMember.util.Rectangle(
            margin_left + horizontal_separator_width,
            vertical_separator - separator_clearance,
            y + separator_clearance,
            y_next - separator_clearance,
        );
        const right = new reMember.util.Rectangle(
            vertical_separator + separator_clearance,
            image.width - margin_right,
            y + separator_clearance,
            y_next - separator_clearance,
        );
        boxes.push([left, right]);
    }
    return [boxes, {
        horizontal_separator_box,
        horizontal_separators,
        vertical_separators_box,
        vertical_separators_candidates,
        vertical_separators,
    }];
}

const extract_card_boundaries = function (config, image, card_boxes) {
    const card_clearance = reMember.util.mm_to_pixels(config, image, config.card_clearance);
    const card_boundaries = [];
    for (const [box_left, box_right] of card_boxes) {
        const card_left = reMember.util.determine_bb_for_box(config, image, box_left, card_clearance);
        const card_right = reMember.util.determine_bb_for_box(config, image, box_right, card_clearance);
        card_boundaries.push([card_left, card_right]);
    }
    return card_boundaries;
}

const extract_card_images = function (image, card_boundaries) {
    const card_images = [];
    for (const [card_boundary_left, card_boundary_right] of card_boundaries) {
        card_images.push([image.crop(card_boundary_left), image.crop(card_boundary_right)]);
    }
    return card_images;
}

window.reMember.extract_flashcards = function (config, image) {
    let debug_info = {};
    try {
        reMember.util.step_progress("extract-card-boxes");
        const [card_boxes, new_debug_info] = extract_card_boxes(config, image);
        debug_info = {...debug_info, ...new_debug_info, card_boxes};
        reMember.util.step_progress("extract-card-boundaries");
        const card_boundaries = extract_card_boundaries(config, image, card_boxes);
        debug_info = {...debug_info, card_boundaries};
        reMember.util.step_progress("extract-card-images");
        const card_images = extract_card_images(image, card_boundaries);
        debug_info = {...debug_info, card_images};
        reMember.util.step_progress("make-flashcards");
        const flashcards = [];
        for (const [left, right] of card_images) {
            const flashcard = new reMember.anki.Flashcard(left, right);
            if (config.switch_front_back) {
                flashcard.switch();
            }
            flashcards.push(flashcard);
        }
        return [flashcards, debug_info];
    } catch (error) {
        throw new reMember.util.ReMemberError(error, debug_info);
    }
}
