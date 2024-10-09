import {test, expect} from "vitest";
import {Cache} from "./cache";


class TestData {
    public x: number;

    constructor(x: number) {
        this.x = x;
    }
}


class TestCache extends Cache<TestData> {
    private promise_fails: boolean;
    private decode_fails: boolean;

    constructor(promise_fails: boolean = false, decode_fails: boolean = false) {
        super();
        this.promise_fails = promise_fails;
        this.decode_fails = decode_fails;
    }

    get_raw_promise(): Promise<number> {
        if ( this.promise_fails ) {
            return Promise.reject('Failure')
        } else {
            return Promise.resolve(3.1415);
        }
    }

    decode(raw: number): TestData {
        if ( this.decode_fails ) {
            throw new Error('Failed')
        } else {
            return new TestData(raw)
        }
    }
}



test('Cache - good', async () => {
    const c = new TestCache();
    const data1 = await c.get_data();
    expect(data1.x).toBe(3.1415);
    const data2 = await c.get_data();
    expect(data2.x).toBe(3.1415);
});
