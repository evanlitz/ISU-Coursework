import 'bootstrap/dist/css/bootstrap.css';
import { Container, Card } from 'react-bootstrap';


// export function UserCard(props) {
//   return ( <Container className="p-4"> ... </Container> );
// }

export function UserCard({ picture, name, amount, married, address }) {
  return (
    <Card style={{ width: "26rem" }} className="shadow-sm">  
      <Card.Img
        variant="top"
        src={picture}
        style={{ width: "100%", height: "260px", objectFit: "cover" }}
      />
      <Card.Body>
        <Card.Title className="mb-3">{name}</Card.Title>

        {}
        <Card.Text><strong>Salary:</strong> $ {amount}</Card.Text>
        <Card.Text><strong>Married:</strong> {married ? "Yes" : "No"}</Card.Text>

        {}
        <Card.Text className="mb-0">
          <strong>Address:</strong> {address.street}, {address.city}, {address.state}
        </Card.Text>
      </Card.Body>
    </Card>
  );
}