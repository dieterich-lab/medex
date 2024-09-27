function get_label(default_label: string, custom_label?: string): string {
    if ( !custom_label ) {
        return default_label;
    } else {
        return custom_label.replace(/%DEFAULT%/g, default_label);
    }
}

function capitalize(x: string) {
    return x[0].toUpperCase() + x.slice(1);
}

export {get_label, capitalize};
