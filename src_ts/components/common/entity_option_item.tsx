import {ChangeEventHandler, JSX} from "react";
import {Entity} from "../../services/entity";

interface EntityOptionItemProps {
	checked: boolean,
	disabled: any;
	onClick: ChangeEventHandler<HTMLDivElement> | undefined;
	option: { value: Entity };
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
			<MyEntityItem entity={props.option.value}/>
		</div>
	);
}

interface MyEntityItemProps {
	entity: Entity,
}

function MyEntityItem(props: MyEntityItemProps): JSX.Element {
	const entity = props.entity;
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