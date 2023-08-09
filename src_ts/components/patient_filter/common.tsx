import {Entity} from '../../services/entity';

interface PatientFilterComponentProps {
    refresh_filters: () => void,
}

interface PatientFilterEntityDetailsProps extends PatientFilterComponentProps {
    entity: Entity,
    measurement: string|null,
}

export {PatientFilterComponentProps, PatientFilterEntityDetailsProps};
