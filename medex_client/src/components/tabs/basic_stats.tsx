import {Card, Tab, Tabs} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import {DatabaseStats} from "./basic_stats/database_stats";
import {EntityStats} from "./basic_stats/entity_stats";
import {TabFrame} from "./common/frame";
import {EntityType} from "../../services/entity";

function BasicStats() {
    return (
        <TabFrame>
            <Card>
                <Tabs defaultActiveKey="Database">
                    <Tab eventKey="Database" title="Database">
                        <DatabaseStats/>
                    </Tab>
                    <Tab eventKey="Numerical" title="Numerical">
                        <EntityStats entityType={EntityType.NUMERICAL}/>
                    </Tab>
                    <Tab eventKey="Categorical" title="Categorical">
                        <EntityStats entityType={EntityType.CATEGORICAL}/>
                    </Tab>
                    <Tab eventKey="Date" title="Date">
                        <EntityStats entityType={EntityType.DATE}/>
                    </Tab>
                </Tabs>
            </Card>
        </TabFrame>
    );
}

export {BasicStats};