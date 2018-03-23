import React from 'react';
import { connect } from 'react-redux'
import { submitContactForm } from '../actions/contact';
import Messages from './Messages';
import Webcam from 'react-webcam';

class Contact extends React.Component {
  constructor(props) {
    super(props);
    this.state = { name: '', email: '', message: '', screenshot: '' };
  }

  handleChange(event) {
    this.setState({ [event.target.name]: event.target.value });
  }

  handleSubmit(event) {
    event.preventDefault();
    const screenshot = this.webcam.getScreenshot();
    this.props.dispatch(submitContactForm(this.state.name, this.state.email, this.state.message, this.state.screenshot ));
  }

  render() {
    return (
      <div className="container">
        <div className="panel">
          <div className="panel-heading">
            <h3 className="panel-title">Contact Form</h3>
          </div>
          <div className="panel-body">
            <Messages messages={this.props.messages}/>
            <form onSubmit="http://13.59.101.92:8000/mine" method="post" enctype="multipart/form-data" className="form-horizontal">
              <div className="form-group">
                <label htmlFor="name" className="col-sm-2">Name</label>
                <div className="col-sm-8">
                  <input type="text" name="name" id="name" className="form-control" value={this.state.name} onChange={this.handleChange.bind(this)} autoFocus/>
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="email" className="col-sm-2">Email</label>
                <div className="col-sm-8">
                  <input type="email" name="email" id="email" className="form-control" value={this.state.email} onChange={this.handleChange.bind(this)}/>
                </div>
              </div>
              <div className="form-group">
              </div>
              <div className="form-group">
              <label htmlFor="message" className="col-sm-2">Body</label>
              <div className="col-sm-8">
                <Webcam
                  ref={node => this.webcam = node}
                  audio={false}
                  height={350}
                  screenshotFormat="image/jpeg"
                  width={350}
                />
              </div>


              <div>
                <h2>Screenshots</h2>
                <div className='screenshots'>
                  <div className='controls'>
                    <button onClick={this.handleClick}>capture</button>
                  </div>
                  {this.state.screenshot ? <img src={this.state.screenshot} /> : null}
                </div>
              </div>


              </div>
	      <input type="file" name="file" capture="camera" accept="image/*"><BR>
              <div className="form-group">
                <div className="col-sm-offset-2 col-sm-8">
                  <button type="submit" className="btn btn-success">Send</button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  return {
    messages: state.messages
  };
};

export default connect(mapStateToProps)(Contact);
