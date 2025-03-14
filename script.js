"use strict";

initSqlJs().then(function (sql) {
    window.SQL = sql;
});

const draw = function (ctx, box, color, alpha, mode) {
    if (!box) return;
    ctx.fillStyle = color + Math.ceil(alpha * 255).toString(16).toUpperCase();
    ctx.strokeStyle = color + Math.ceil(alpha * 255).toString(16).toUpperCase();
    switch (mode) {
        case "box":
            ctx.fillRect(box.x1, box.y1, box.width, box.height);
            break;
        case "line":
            ctx.beginPath();
            ctx.moveTo(box.x1, box.y1);
            ctx.lineTo(box.x2, box.y2);
            ctx.stroke();
            break;
        default:
            throw new Error(`invalid draw mode '${mode}'`);
    }
}

const show_preview = function (config, image, debug_info) {
    if (!config.debug) return;

    const canvas = document.querySelector("#preview-canvas");
    canvas.width = image.width;
    canvas.height = image.height;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(image, 0, 0);
    draw(ctx, debug_info.horizontal_separator_box, "#FF0000", .2, "box");
    if (debug_info.horizontal_separator_box && debug_info.horizontal_separators) {
        for (const horizontal_separator of debug_info.horizontal_separators) {
            draw(
                ctx,
                new reMember.util.Rectangle(
                    debug_info.horizontal_separator_box.x1,
                    debug_info.horizontal_separator_box.x2,
                    horizontal_separator,
                    horizontal_separator,
                ),
                "#FF0000",
                1,
                "line",
            );
        }
    }
    if (debug_info.vertical_separators_box) {
        for (const box of debug_info.vertical_separators_box) {
            draw(ctx, box, "#00FF00", .2, "box");
        }
        if (debug_info.vertical_separators_candidates) {
            if (debug_info.vertical_separators_box.length !== debug_info.vertical_separators_candidates.length)
                throw Error("inconsistent data in debug info")
            for (let i = 0; i < debug_info.vertical_separators_box.length; i++) {
                const box = debug_info.vertical_separators_box[i];
                const candidates = debug_info.vertical_separators_candidates[i];
                for (const candidate of candidates) {
                    draw(
                        ctx,
                        new reMember.util.Rectangle(
                            candidate,
                            candidate,
                            box.y1,
                            box.y2,
                        ),
                        "#00FF00",
                        1,
                        "line",
                    );
                }
            }
        }
    }
    for (const box of [].concat(...(debug_info.card_boxes || []), ...(debug_info.card_boundaries || []))) {
        draw(ctx, box, "#0000FF", .2, "box");
    }

    document.querySelector("#preview-placeholder").classList.add("d-none");
    const numCards = document.querySelector("#preview-num-cards");
    numCards.innerHTML = `${(debug_info.card_boxes || []).length} Cards`;
    numCards.classList.remove("d-none");
    canvas.classList.remove("d-none");
};

const make_processor = function (config, image) {
    const handle_error = function (error) {
        alert(error);
        console.error(error);
        if (error instanceof reMember.util.ReMemberError) {
            show_preview(config, image, error.debug_info);
        }
    };

    return function () {
        try {
            const [flashcards, debug_info] = reMember.extract_flashcards(
                config,
                reMember.util.Image.from_html_image(image),
            );
            show_preview(config, image, debug_info);
            reMember.util.step_progress("write-anki-package");
            reMember.anki.write_to_package(config, flashcards).catch(handle_error).then(function () {
                reMember.util.step_progress("download");
            });
        } catch (error) {
            handle_error(error);
        }
    };
};


window.onload = function () {
    const config = new reMember.Config(
        156.986, // rM-Portrait
        4.80798 / 2,  // half box
        3 * 4.80798,
        0,
        0,
        11.72093,
        4.80798,
        4.80798,
        4.80798 / 2,  // === separator_clearance
        191,
        0.2,
        true,
        true,
        true,
        reMember.util.random_int(1 << 30, 1 << 31),
        "reMember",
        "reMember.apkg",
        true,
    );

    const image = new Image();
    let image_loaded = false;
    const process = make_processor(config, image);

    image.addEventListener("load", function () {
        image_loaded = true;
        process();
    });

    const reader = new FileReader();
    reader.addEventListener("load", function (event) {
        image_loaded = false;
        image.src = event.target.result;
    });

    const input = document.querySelector("#file");
    input.addEventListener("change", function () {
        reMember.util.reset_progress({
            "init": "",
            "load-image": "Loading image",
            "extract-card-boxes": "Extracting card boxes",
            "extract-card-boundaries": "Extracting card boundaries",
            "extract-card-images": "Extracting card images",
            "make-flashcards": "Making flashcards",
            "write-anki-package": "Writing Anki package",
            "download": "Initiating download",
        });
        reMember.util.step_progress("load-image");
        reader.readAsDataURL(input.files[0]);
        return false;
    });
};
