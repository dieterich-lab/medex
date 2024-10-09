abstract class Cache<T> {
    private promise: Promise<unknown> | null;
    private data: T | null;

    constructor() {
        this.promise = null;
        this.data = null;
    }

    abstract get_raw_promise(): Promise<unknown>;

    abstract decode(raw: unknown): T;

    public async get_data(): Promise<Readonly<T>> {
        if ( this.data === null ) {
            if ( this.promise === null) {
                this.promise = this.get_raw_promise();
            }
            this.data = this.decode(await this.promise);
        }
        return this.data;
    }
}

export {Cache};