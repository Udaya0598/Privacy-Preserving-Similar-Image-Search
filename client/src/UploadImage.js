import React, { useState } from "react";
import ReactDOM from "react-dom";
import "antd/dist/antd.css";
import "./index.css";
import { Upload, message, Button, Image, PageHeader, Tag, Typography } from "antd";
import { UploadOutlined, InboxOutlined } from "@ant-design/icons";
import { useHistory } from "react-router-dom";

const { Dragger } = Upload;
const { Title } = Typography;

const UploadBtn = (ownProps) => {
  const [imageList, setImageList]=useState([]);

  const handleChange = info => {
    let fileList = [...info.fileList];

    console.log('fileList--',fileList);
    // 1. Limit the number of uploaded files
    // Only to show two recent uploaded files, and old ones will be replaced by the new
    // fileList = fileList.slice(-2);

    // 2. Read from response and show file link
    fileList = fileList.map(file => {
      if(file.error && file.error.status == 500){
        message.error('Uploading Image Failed!');
      } else {
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
      }
      return file;
    });

    // setImageeList({ fileList });
  };

  const endpoint = "upload"

  const props = {
    name: "image",
    action: "http://localhost:5000/" + endpoint,
    onChange: handleChange,
    accept:"image/*",
    multiple: ownProps.batch
  };

  console.log('filList', imageList);

  if(ownProps.batch){
    return (
      <div style={{ width: 720 }}>
        <Dragger {...props}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag file to this area to upload</p>
          <p className="ant-upload-hint">
            Support for a single or bulk upload. Only Images are supported.
          </p>
        </Dragger>
      </div>
    );
  }

  return (
    <Upload {...props}>
      <Button icon={<UploadOutlined />}>Select Image</Button>
      {
        imageList.map(img => img.url).filter(url => !!url).length > 0 && (
          <div>
            <h2>
              Image Uploaded Successfully
            </h2>
            <div style={{ margin: 4 }}>
              {
                imageList.map(img => <Image src={img.url}/>)
              }
            </div>
          </div>
        )
      }
    </Upload>
  );
};

const UploaduBtton = (props) => {
  const [imageList, setImageList]=useState([]);

  const history = useHistory();

  function handleClick() {
    history.push("/similar");
  }

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

  return (
    <div>
        <PageHeader
          ghost={false}
          // onBack={() => window.history.back()}
          avatar={{ src: 'https://www.gstatic.com/images/branding/product/1x/google_cloud_search_512dp.png' }}
          title={"Image Search and Retrieval"}
          subTitle="Privacy preserving image sharing in social media"
          // tags={<Tag color="blue">Beta</Tag>}
          extra={[
            <Button key="1" type="primary" onClick={handleClick}>
              Find Similar Images
            </Button>,
            ...(props.batch ? [
              <Button key="1" type="primary" onClick={() => {
                history.push("/upload");
              }}>
                Upload
              </Button>
            ]:[
              <Button key="1" type="primary" onClick={() => {
                history.push("/batch-upload");
              }}>
                Batch Upload
              </Button>
            ])
          ]}
        >
          <Typography>
            <Title>
              {props.batch ? "Batch Upload" : "Upload"}
            </Title>
          </Typography>
          <UploadBtn batch={props.batch} />
        </PageHeader>
      </div>
  );
};

export default UploaduBtton;
