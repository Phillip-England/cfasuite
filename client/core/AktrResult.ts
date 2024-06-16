


export class AktrResult {

	value: any
	err: Error | null;

	constructor() {
		this.value = null
		this.err = null;
	}

	async new(operation: Function): Promise<AktrResult> {
		try {
			await operation();
		} catch (err: unknown) {
			this.err = err as Error;
		}
		return this;
	}

	isOk(): boolean {
		return this.err === null;
	}

	isErr(): boolean {
		return this.err !== null;
	}

	unwrap(): any {
		if (this.err !== null) {
			throw this.err;
		}
		return this.value;
	}

}