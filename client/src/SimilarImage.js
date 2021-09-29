import { Image } from "antd";
import React, { useState } from "react";
// import getSimilarImages from "./server";
import ReactDOM from "react-dom";
import "antd/dist/antd.css";
import "./index.css";
import { Upload, message, Button, PageHeader, Tag, Typography } from "antd";
import axios from 'axios';
import { UploadOutlined } from "@ant-design/icons";

import { Router, Route, Link, browserHistory, IndexRoute, withRouter } from "react-router";

const { Title } = Typography;

const UploadBtn = () => {
  const [imageList, setImageList]=useState([]);

  const handleChange = info => {
    let fileList = [...info.fileList];

    console.log('fileList--',fileList);
    // 1. Limit the number of uploaded files
    // Only to show two recent uploaded files, and old ones will be replaced by the new
    // fileList = fileList.slice(-2);

    // 2. Read from response and show file link
    fileList = fileList.map(file => {
      if (file.response) {
        console.log('file --', file);
        // Component will show file.url as link
        file.url = file.response.url;
        const resObj = {
          url: file.response.query_image_address,
          name: file.name,
          similar_images: file.response.similar_images,
        };
        setImageList([...imageList, resObj]);
      }
      return file;
    });

    // setImageeList({ fileList });
  };

  const props = {
    name: "image",
    action: "http://localhost:5000/similar",
    onChange: handleChange,
    // onChange(info) {
    //   console.log('info--', info);

    //   if (info.file.status !== "uploading") {
    //     console.log(info.file, info.fileList);
    //   }
    //   if (info.file.status === "done") {
    //     setImageeList([...imageList, {

    //     }])
    //     message.success(`${info.file.name} file uploaded successfully`);
    //   } else if (info.file.status === "error") {
    //     message.error(`${info.file.name} file upload failed.`);
    //   }
    // }

  };

  console.log('filList', imageList);

  return (
    <Upload {...props}>
      <Button icon={<UploadOutlined />}>Select Image</Button>
      {
        imageList.length > 0 && (
          <div>
            <h2>
              Query Image
            </h2>
            <Image src={imageList[0].url}/>
            <h2>Similar Images</h2>
            {imageList[0].similar_images.map((image) => (
              <Image width={200} src={image.address} style={{ margin: 8 }} />
            ))}
          </div>
        )
      }
    </Upload>
  );
};

class ImageSimilar extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      similarImages: []
    };
  }

  componentDidMount(){
    // this.getSimilarImages()
  }

  getSimilarImages = () => {
    let similarImages = []
    const baseUrl = 'http://localhost:5000'
    console.log('sending request');
    
    axios.get(`${baseUrl}/fetch-similar-images`).then(res => {
      console.log('recieved response');
      console.log('similar images', res.data);
      this.setState({
        'similarImages': res.data,
      })
    })
  
    console.log('returning response', similarImages);
    return similarImages;
  }  
  
  handleClick = (route) => {
    this.props.history.push(route);
  }

  render() {
    return (
      <div>
        <PageHeader
          ghost={false}
          // onBack={() => window.history.back()}
          avatar={{ src: 'https://www.gstatic.com/images/branding/product/1x/google_cloud_search_512dp.png' }}
          title={"Image Search and Retrieval"}
          tags={<Tag color="blue">Beta</Tag>}
          subTitle="Privacy preserving image sharing in social media"
          extra={[
            <Button key="1" type="primary" onClick={() => this.handleClick('/upload')}>
              Upload
            </Button>,
            <Button key="1" type="primary" onClick={() => this.handleClick('/batch-upload')}>
              Batch Upload
            </Button>
          ]}
        >
          <Typography>
            <Title>
              {this.props.batch ? "Batch Upload" : "Upload"}
            </Title>
          </Typography>
          <UploadBtn />
        </PageHeader>
      </div>
    );
  }
}
export default withRouter(ImageSimilar);

