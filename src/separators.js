"use strict";

if (!window.reMember) {
    window.reMember = {};
}

window.reMember.separators = {
    extract(config, image, transpose) {
        const matrix = transpose ? reMember.util.transpose(image.bw_data) : image.bw_data;
        const ys = [];
        let current_ys = [];
        for (let y = 0; y <= matrix.length; y++) {
            const is_separator = y < matrix.length && matrix[y].filter(c => c <= config.black_threshold).length / matrix[y].length > config.separator_threshold;
            if (is_separator) {
                current_ys.push(y);
            } else if (current_ys.length > 0) {
                ys.push(Math.round(current_ys.reduce((a, b) => a + b) / current_ys.length));
                current_ys = [];
            }
        }
        return ys;
    },
    extract_from_box(config, image, box, transpose) {
        return reMember.separators.extract(config, image.crop(box), transpose);
    }
};
