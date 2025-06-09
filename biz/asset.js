

import path from 'path';
import { remark } from 'remark';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import fs from 'fs';
import * as fsPromise from 'fs/promises';

import { UploadImage } from './upload_image_asset.js';


const filePath = '/Users/pranavreddy/Desktop/RNConvertion/output_jsons/mmd_clean_up.json';
const cycFilePath = "/Users/pranavreddy/Desktop/RNConvertion/output_jsons/cyc_cya.json";
const finaloutputPath = '/Users/pranavreddy/Desktop/RNConvertion/output_jsons/final_list_output.json';

const contentId = process.argv[2]; // 0 = node, 1 = script name, 2 = first user arg

console.log("Received content ID:", contentId);

const resultArray = [];

async function processFile(filePath, title,posn) {
    function parseTextWithLatex(text) {
        const latexRegex = /\$(.*?)\$/g; // Regex to detect LaTeX equations between $
        let formattedText = [];
        let lastIndex = 0;
        
        // Match LaTeX equations
        let match;
        while ((match = latexRegex.exec(text)) !== null) {
          // Text before LaTeX equation
          if (match.index > lastIndex) {
            formattedText.push({
              type: 'text',
              text: text.slice(lastIndex, match.index)
            });
          }
          // LaTeX equation (inline)
          formattedText.push({
            type: 'katex',
            equation: match[1].trim(),
            inline: true, // Ensure it's inline
            version: 1
          });
          lastIndex = latexRegex.lastIndex;
        }
        
        // Add the remaining part of the text after the last match
        if (lastIndex < text.length) {
          formattedText.push({
            type: 'text',
            text: text.slice(lastIndex)
          });
        }
    
        return formattedText;
    }

    const fileData = await fs.promises.readFile(filePath, 'utf-8');
    const lines = fileData.split('\n');
  
    let questionText = '';
    let answerText = '';
  
    // Extract question from lines starting with '##', answer from other lines
    lines.forEach((line) => {
      if (line.startsWith('##')) {
        questionText += line.replace('##', '').trim() + ' ';
      } else {
        answerText += line.trim() + ' ';
      }
    });
  
    questionText = questionText.trim();
    answerText = answerText.trim();

    console.log("trimmed que and ans text");

    const questionFormatted = parseTextWithLatex(questionText);
    const answerFormatted = parseTextWithLatex(answerText);

  
    // Build lexical JSON structure
    const lexicalJson = {
      configData: {
        version: 1,
        format: 'LEXICAL',
        question: {
          configData: {
            root: {
              children: [
                {
                  type: 'paragraph',
                  direction: 'ltr',
                  format: '',
                  indent: 0,
                  version: 1,
                  textFormat: 0,
                  textStyle: '',
                  children: questionFormatted,
                  tag: 'p',
                  id: '',
                },
              ],
              direction: 'ltr',
              format: '',
              indent: 0,
              type: 'root',
              version: 1,
            },
          },
        },
        answer: {
          configData: {
            root: {
              children: [
                {
                  type: 'paragraph',
                  direction: 'ltr',
                  format: '',
                  indent: 0,
                  version: 1,
                  textFormat: 0,
                  textStyle: '',
                  children: answerFormatted,
                  tag: 'p',
                  id: '',
                },
              ],
              direction: 'ltr',
              format: '',
              indent: 0,
              type: 'root',
              version: 1,
            },
          },
        },
      },
    };
  
    const fileNameWithoutExt = path.basename(filePath, path.extname(filePath));
    const compositeFileName = `${title}_${fileNameWithoutExt}`;
  
    const finalOutput = {
      fileName: compositeFileName,
      type: 'QUESTION',
      tags: 'EXERCISE',
      pos: posn,
      jsonData: JSON.stringify(lexicalJson),
    };
  
    console.log('at file creation');

    resultArray.push(finalOutput);
}

async function convertToLexicalJSON(ast) {
    const lexicalDocument = { children: [] };

    for (const node of ast.children) {
        const convertedNodes = await convertMarkdownNodeToLexicalNode(node);
        if (convertedNodes) {
            if (Array.isArray(convertedNodes)) {
                lexicalDocument.children.push(...convertedNodes);
            } else {
                lexicalDocument.children.push(convertedNodes);
            }
        }
    }

    return lexicalDocument;
}

async function convertMarkdownNodeToLexicalNode(node) {
    console.log(`convertMarkdownNodeToLexicalNode this called for ${node.type}`)
    if (node.type === 'image') {
        console.log("came to image part in default type")
        const image_url = await UploadImage(node.url,contentId);
        return {
            type: 'image',
            src: image_url,
            altText: node.alt || '',
            caption: {
                editorState: {
                    root: {
                        children: [],
                        direction: null,
                        format: "",
                        indent: 0,
                        type: "root",
                        version: 1
                    }
                }
            },
            height: 0,
            maxWidth: 500,
            showCaption: false,
            width: 0,
            version: 1
        };
    }
    if (node.type === 'html' && node.value.match(/<img\s+src=["']([^"']+)["'][^>]*>/)) {
        console.log("came to html type ")
        const imgUrlMatch = node.value.match(/<img\s+src=["']([^"']+)["'][^>]*>/);
        let imgUrl = imgUrlMatch ? imgUrlMatch[1] : '';
        if(imgUrl!==""){
            let allen_url = await UploadImage(imgUrl,contentId);
            if(allen_url !=="")
            {
                imgUrl = allen_url
            }
        }

        console.log(imgUrl)

        const altTextMatch = node.value.match(/<img\s+alt=["']([^"']+)["'][^>]*>/);
        let altText = altTextMatch ? altTextMatch[1] : '';
        // Extract caption from <figcaption> if present
        const captionMatch = node.value.match(/<figcaption>(.*?)<\/figcaption>/);
        if (captionMatch && captionMatch[1].trim()) {
          altText = captionMatch[1].trim();
        }

        return {
            type: 'image',
            src: imgUrl,
            altText: altText,
            caption: {
                editorState: {
                    root: {
                        children: [],
                        direction: null,
                        format: "",
                        indent: 0,
                        type: "root",
                        version: 1
                    }
                }
            },
            height: 0,
            maxWidth: 500,
            showCaption: false,
            width: 0,
            version: 1
        };
    }
    switch (node.type) {
        case 'text':
            return {
                type: 'text',
                text: node.value,
                format: 0,
                detail: 0,
                mode: 'normal',
                style: '',
                version: 1
            };
        case 'inlineCode':
            return {
                type: 'text',
                text: node.value,
                format: 1,
                detail: 0,
                mode: 'normal',
                style: '',
                version: 1
            };
        case 'inlineMath':
        case 'math':
            return {
                type: 'katex',
                equation: node.value,
                inline: true,
                version: 1
            };
        case 'emphasis':
        case 'strong':
            return {
                type: 'paragraph',
                children: await Promise.all(node.children.map(convertMarkdownNodeToLexicalNode)),
                direction: 'ltr',
                format: '',
                indent: 0,
                version: 1
            };
        case 'link':
            return {
                type: 'link',
                url: node.url,
                children: await Promise.all(node.children.map(convertMarkdownNodeToLexicalNode)),
                direction: 'ltr',
                format: '',
                indent: 0,
                version: 1
            };
        case 'list':
            return {
                type: 'list',
                direction: 'ltr',
                format: '',
                indent: 0,
                version: 1,
                listType: node.ordered ? 'ordered' : 'bullet',
                start: node.start || 1,
                tag: node.ordered ? 'ol' : 'ul',
                children: await Promise.all(node.children.map((item, index) => convertListItemToLexicalNode(item, index + 1))),
            };
        case 'table':
            return {
                type: 'wrapper',
                direction: null,
                format: '',
                indent: 0,
                version: 1,
                tag: 'div',
                scrollable: true,
                children: [
                    {
                        type: 'table',
                        direction: null,
                        format: '',
                        indent: 0,
                        version: 1,
                        children: await Promise.all(
                            node.children.map(async row => ({
                                type: 'tablerow',
                                direction: null,
                                format: '',
                                indent: 0,
                                version: 1,
                                children: await Promise.all(
                                    row.children.map(async cell => ({
                                        type: 'tablecell',
                                        direction: null,
                                        format: '',
                                        indent: 0,
                                        version: 1,
                                        backgroundColor: null,
                                        colSpan: 1,
                                        headerState: 0,
                                        rowSpan: 1,
                                        children: await Promise.all(
                                            cell.children.map(async d => ({
                                                type: 'paragraph',
                                                direction: 'ltr',
                                                format: '',
                                                indent: 0,
                                                version: 1,
                                                textFormat: 0,
                                                textStyle: '',
                                                children: [await convertMarkdownNodeToLexicalNode(d)]
                                            }))
                                        )
                                    }))
                                )
                            }))
                        )
                    }
                ]
                
            };
        case 'heading':
            return {
                type: 'heading',
                direction: 'ltr',
                format: '',
                indent: 0,
                version: 1,
                tag: `h${node.depth}`,
                id: `${node.depth}.0`,
                children: [{
                    type: 'text',
                    text: node.children.map(child => child.value).join(''),
                    format: node.depth === 1 ? 1 : 0,
                    detail: 0,
                    mode: 'normal',
                    style: '',
                    version: 1
                }]
            };
        case 'paragraph':
            const childrenPromises = await Promise.all(node.children.map(convertMarkdownNodeToLexicalNode));
            return {
                type: 'paragraph',
                direction: 'ltr',
                format: '',
                indent: 0,
                version: 1,
                textFormat: 0,
                textStyle: '',
                children: childrenPromises.flat()
            };
        default:
            console.warn(`Unhandled node type: ${node.type}`);
            return {
                type: 'text',
                text: '',
                format: 0,
                detail: 0,
                mode: 'normal',
                style: '',
                version: 1
            };
    }
}

async function convertListItemToLexicalNode(node, value) {
    return {
        type: 'listitem',
        direction: 'ltr',
        format: '',
        indent: 0,
        version: 1,
        value: value,
        children: await Promise.all(node.children.map(convertMarkdownNodeToLexicalNode))
    };
}

async function parseMmdToLexicalJson(inputFilePath, posn, title) {
  try {
    const mmdContent = await fsPromise.readFile(inputFilePath, 'utf-8');

    console.log("read mmd content ")

    // Regex to match \section*{Title} and its content until next \section* or EOF
    const sectionRegex = /\\section\*\{([^}]+)\}\s*([\s\S]*?)(?=\\section\*|$)/g;

    const qaPairs = [];
    let match;
    while ((match = sectionRegex.exec(mmdContent)) !== null) {
      const sectionContent = match[2].trim();
      console.log("match found");

      // Extract subsection content as answer
      const subsecMatch = /\\subsection\*\{([^}]+)\}\s*([\s\S]*)/m.exec(sectionContent);

      let questionText = '';
      let answerText = '';

      if (subsecMatch) {
        questionText = sectionContent.slice(0, subsecMatch.index).trim();
        answerText = subsecMatch[2].trim();
      } else {
        questionText = sectionContent;
        answerText = '';
      }

      qaPairs.push({ questionText, answerText });
    }

    if (qaPairs.length === 0) {
      console.error('No valid Q&A pairs found in:', inputFilePath);
      return;
    }

    console.log("running function");

    // Helper to create lexical paragraph node
    function makeParagraphNode(text) {
      return {
        type: 'paragraph',
        direction: 'ltr',
        format: '',
        indent: 0,
        version: 1,
        textFormat: 0,
        textStyle: '',
        children: [
          {
            type: 'text',
            text: text,
            format: 0,
            detail: 0,
            mode: 'normal',
            style: '',
            version: 1,
          },
        ],
        tag: 'p',
        id: '',
      };
    }

    // For simplicity, take only the first Q&A pair
    const { questionText, answerText } = qaPairs[0];

    const outputJson = {
      configData: {
        version: 1,
        format: 'LEXICAL',
        question: {
          configData: {
            root: {
              children: [makeParagraphNode(questionText)],
              direction: 'ltr',
              format: '',
              indent: 0,
              type: 'root',
              version: 1,
            },
          },
        },
        answer: {
          configData: {
            root: {
              children: [makeParagraphNode(answerText)],
              direction: 'ltr',
              format: '',
              indent: 0,
              type: 'root',
              version: 1,
            },
          },
        },
      },
    };

    // const fileNameRaw = path.basename(inputFilePath, path.extname(inputFilePath));
    // const safeFileName = fileNameRaw.replace(/[^a-z0-9]/gi, '_').toLowerCase();

    const finalOutput = {
      fileName: title,
      type: 'QUESTION',
      tags: 'EXERCISE',
      pos: posn,
      jsonData: JSON.stringify(outputJson),
    };

    // Ensure output folder exists
    // await fsPromise.mkdir(outputFolderPath, { recursive: true });

    // const outputFilePath = path.join(outputFolderPath, `${safeFileName}.entity.json`);
    // await fsPromise.writeFile(outputFilePath, JSON.stringify(finalOutput, null, 2));

    resultArray.push(finalOutput);

    //console.log(`Saved entity for file "${fileNameRaw}" to ${outputFilePath}`);
  } catch (error) {
    console.error(`Error processing file "${inputFilePath}":`, error);
  }
}



async function CreateStringifyJson(){
    const data = fs.readFileSync(filePath, 'utf8');
    const jsonData = JSON.parse(data);

    const chunks = jsonData;
  
    for (let i = 0; i < chunks.length; i++) {
        var inputFilePath = chunks[i]["file_path"]
    // console.log(inputFilePath)

        let fileData;
        try {

          fileData = fs.readFileSync(inputFilePath, "utf8");
          const firstSectionIndex = fileData.indexOf('\\section*{');
          if (firstSectionIndex === -1) {
            console.warn(`No \\section*{} found in file ${file}, skipping.`);
            return;
          }
          fileData = fileData.slice(firstSectionIndex).trim();

        } catch (error) {
            console.error(`Error reading file ${inputFilePath}: ${error.message}`);
            break
        }

        console.log(`type is ${chunks[i]["type"]}`);
        let posn = chunks[i]["pos"]

        if(chunks[i]["type"]==="DEFAULT"){
            const sections = fileData.split(/(?=\\section\*\{)/g);

            // console.log(sections)

            for (const [index, section] of sections.entries()) {
                const sectionTitleMatch = section.match(/\\section\*\{([^}]+)\}/);
                console.log(`section title ${sectionTitleMatch}`);
                if (sectionTitleMatch === null) {
                    continue;
                }
            
                const sectionTitle = sectionTitleMatch[1];
                const contentWithoutSectionLine = section.replace(/\\section\*\{[^}]+\}\n?/, '').trim();
            
                const ast = remark()
                    .use(remarkParse)
                    .use(remarkMath)
                    .use(remarkGfm)
                    .parse(contentWithoutSectionLine);
            
                const lexicalJSON = await convertToLexicalJSON(ast);
            
                const entity = {
                    fileName: sectionTitle,
                    type: "TEXT",
                    pos: posn,
                    jsonData: JSON.stringify({
                        root: {
                            children: lexicalJSON.children,
                            direction: 'ltr',
                            format: '',
                            indent: 0,
                            type: 'root',
                            version: 1
                        }
                    })
                };
            
                resultArray.push(entity);
            }
            
        }
        else if(chunks[i]["type"] === "CB") { //change here to CB
            await parseMmdToLexicalJson(inputFilePath,posn,chunks[i]["title"]);
        }
    }


    const cycdata = fs.readFileSync(cycFilePath, 'utf8');
    const cycjsonData = JSON.parse(cycdata);

    const cycChunks = cycjsonData;

    for(let i=0;i<cycChunks.length;i++)
    {
        const queList = cycChunks[i]["que_list"]
        console.log(cycChunks[i]["title"])
        //console.log(queList)
        for(let j=0;j<queList.length;j++)
        {
            await processFile(queList[j]["file_path"],cycChunks[i]["title"],cycChunks[i]["pos"])
        }
    }




    resultArray.sort((a, b) => a.pos - b.pos)

    try {
        fs.writeFileSync(finaloutputPath, JSON.stringify(resultArray, null, 2), 'utf8');
        console.log('JSON file created successfully at', finaloutputPath);
    } catch (error) {
        console.error('Error writing JSON file:', error);
    }
}

CreateStringifyJson()


