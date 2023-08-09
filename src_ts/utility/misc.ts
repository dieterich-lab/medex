function get_label(default_label: string, custom_label?: string): string {
    if ( !custom_label ) {
        return default_label;
    } else {
        return custom_label.replace(/%DEFAULT%/g, default_label);
    }
}

export {get_label};
