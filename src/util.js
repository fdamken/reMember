"use strict";

if (!window.reMember) {
    window.reMember = {};
}

class _ReMemberError extends Error {
    constructor(message, debug_info) {
        super(message);
        this.name = "ReMemberError";
        this.debug_info = debug_info;
    }
}

class _Rectangle {
    constructor(x1, x2, y1, y2) {
        this.x1 = x1;
        this.x2 = x2;
        this.y1 = y1;
        this.y2 = y2;
    }

    add(other) {
        const x_shift = other[0];
        const y_shift = other[1];
        return new reMember.util.Rectangle(
            this.x1 + x_shift,
            this.x2 + x_shift,
            this.y1 + y_shift,
            this.y2 + y_shift,
        );
    }

    get width() {
        return this.x2 - this.x1;
    }

    get height() {
        return this.y2 - this.y1;
    }
}

class _Image {
    constructor(rgba_data, bw_data, width, height) {
        this.rgba_data = rgba_data;
        this.bw_data = bw_data;
        this.width = width;
        this.height = height;
    }

    static from_html_image(image) {
        const canvas = document.createElement("canvas");
        canvas.width = image.width;
        canvas.height = image.height;
        const context = canvas.getContext("2d");
        context.drawImage(image, 0, 0);
        const imageData = context.getImageData(0, 0, image.width, image.height).data;
        const rgba_data = [];
        const bw_data = [];
        for (let y = 0; y < image.height; y++) {
            const rgba_data_row = [];
            const bw_data_row = [];
            for (let x = 0; x < image.width; x++) {
                const index = (y * image.width + x) * 4;
                const r = imageData[index];
                const g = imageData[index + 1];
                const b = imageData[index + 2];
                const a = imageData[index + 3];
                rgba_data_row.push([r, g, b, a]);
                bw_data_row.push((0.299 * r + 0.587 * g + 0.114 * b) * (a / 255));
            }
            rgba_data.push(rgba_data_row);
            bw_data.push(bw_data_row);
        }
        return new _Image(rgba_data, bw_data, image.width, image.height);
    }

    async to_png_blob() {
        const data = [];
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                data.push(...this.rgba_data[y][x]);
            }
        }
        const canvas = document.createElement("canvas");
        canvas.width = this.width;
        canvas.height = this.height;
        const context = canvas.getContext("2d");
        context.putImageData(new ImageData(new Uint8ClampedArray(data), this.width, this.height), 0, 0);
        return await new Promise(function (resolve) {
            canvas.toBlob(function (blob) {
                resolve(blob);
            }, "png");
        });
    }

    crop(box) {
        const rgba_data = [];
        const bw_data = [];
        for (let y = 0; y < box.height; y++) {
            rgba_data.push(this.rgba_data[box.y1 + y].slice(box.x1, box.x2));
            bw_data.push(this.bw_data[box.y1 + y].slice(box.x1, box.x2));
        }
        return new _Image(rgba_data, bw_data, box.width, box.height);
    }
}


window.reMember.util = {
    ReMemberError: _ReMemberError,
    Rectangle: _Rectangle,
    Image: _Image,
    determine_bb(config, image) {
        const matrix = image.bw_data;
        let x1 = null;
        let x2 = null;
        for (let x = 0; x < matrix[0].length; x++) {
            const contains_content = matrix.some(row => row[x] <= config.black_threshold);
            if (contains_content) {
                if (x1 === null) {
                    x1 = x;
                } else {
                    x2 = x;
                }
            }
        }
        let y1 = null;
        let y2 = null;
        for (let y = 0; y < matrix.length; y++) {
            const contains_content = matrix[y].some(c => c <= config.black_threshold);
            if (contains_content) {
                if (y1 === null) {
                    y1 = y;
                } else {
                    y2 = y;
                }
            }
        }
        if (x1 === null) throw new Error('x1 is null');
        if (x2 === null) throw new Error('x2 is null');
        if (y1 === null) throw new Error('y1 is null');
        if (y2 === null) throw new Error('y2 is null');
        return new reMember.util.Rectangle(x1, x2, y1, y2);
    },
    determine_bb_for_box(config, image, box, card_clearance) {
        const raw_bounding_box = reMember.util.determine_bb(config, image.crop(box));
        const bounding_box = new reMember.util.Rectangle(
            raw_bounding_box.x1 + box.x1,
            raw_bounding_box.x2 + box.x1,
            raw_bounding_box.y1 + box.y1,
            raw_bounding_box.y2 + box.y1,
        );
        return new reMember.util.Rectangle(
            Math.max(box.x1, bounding_box.x1 - card_clearance),
            Math.min(box.x2, bounding_box.x2 + card_clearance),
            Math.max(box.y1, bounding_box.y1 - card_clearance),
            Math.min(box.y2, bounding_box.y2 + card_clearance),
        );
    },
    transpose(matrix) {
        const matrix_transposed = [];
        for (let x = 0; x < matrix[0].length; x++) {
            const matrix_row = [];
            for (let y = 0; y < matrix.length; y++) {
                matrix_row.push(matrix[y][x]);
            }
            matrix_transposed.push(matrix_row);
        }
        return matrix_transposed;
    },
    mm_to_pixels(config, image, value) {
        return Math.ceil(value / config.page_width * image.width);
    },
    random_int(min, max) {
        return Math.floor(Math.random() * (max - min)) + min;
    },
    random_string(length) {
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYabcdefghijklmnopqrstuvwxzyZ0123456789";
        let result = "";
        for (let i = 0; i < length; i++) {
            result += chars.charAt(reMember.util.random_int(0, chars.length));
        }
        return result;
    },
    progress_steps: null,
    step_progress(step) {
        if (reMember.util.progress_steps === null) {
            throw new Error("reset_progress must be called before step_progress");
        }
        const keys = Object.keys(reMember.util.progress_steps);
        const i = keys.indexOf(step);
        if (i < 0) throw new Error(`step ${step} not in ${reMember.util.progress_steps}`);
        const progress_bar = document.querySelector("#progress-bar");
        console.log(`${i / (keys.length - 1) * 100}%`);
        progress_bar.style.width = `${i / (keys.length - 1) * 100}%`;
        progress_bar.innerHTML = reMember.util.progress_steps[step];
        document.querySelector("#progress").classList.remove("d-none");
    },
    reset_progress(steps) {
        if (!("init" in steps)) throw new Error(`${steps} is missing step 'init'`);
        reMember.util.progress_steps = steps;
        reMember.util.step_progress("init");
    },
}
