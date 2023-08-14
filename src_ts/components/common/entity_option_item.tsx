import {ChangeEventHandler, JSX} from "react";
import {Entity} from "../../services/entity";

interface EntityOptionItemProps {
	checked: boolean,
	disabled: any;
	onClick: ChangeEventHandler<HTMLDivElement> | undefined;
	option: { value: Entity } | null;
	label: string,
}

function EntityOptionItem(props: EntityOptionItemProps): JSX.Element {
	return (
		<div className={props.disabled ? 'item-renderer disabled': 'item-renderer'}>
			<input
				type="checkbox"
				onChange={props.onClick}
				checked={props.checked}
				tabIndex={-1}
				disabled={props.disabled}
			/>
			<MyEntityItem {... props}/>
		</div>
	);
}

function MyEntityItem(props: EntityOptionItemProps): JSX.Element {
	const entity = props?.option?.value;
	if ( !entity ) {
		return <span>{props.label}</span>
	}
	if ( !entity.description ) {
		return <span>{entity.key}</span>;
	}
	return (
		<span>
			{entity.key}
			&nbsp;&nbsp;&nbsp;
			<span className="option_description">
				{entity.description}
			</span>
		</span>
	);
}

export {EntityOptionItem};