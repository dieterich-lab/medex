import {assertEquals} from 'typia';

enum EntityType {
    NUMERICAL = 'Double',
    CATEGORICAL = 'String',
    DATE = 'Date',
}

enum ShowMarker {
    SHOW = '+',
    DONT_SHOW = '',
}

interface Entity {
    key: string,
    type: EntityType,
    synonym: string | null,
    description: string | null,
    unit: string | null,
    show: ShowMarker | null,
    categories: string[] | null,
    min: number | null,
    max: number | null,
}

function to_entities(raw: unknown): Entity[] {
    return assertEquals<Entity[]>(raw);
}

export {
    to_entities, type Entity, EntityType, ShowMarker
};
