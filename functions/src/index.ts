import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';
// import { makeExecutableSchema } from 'graphql-tools'
// const express = require('express')
// const bodyParser = require('body-parser')
// const { ApolloServer, gql } = require('apollo-server-express')
//import { printSchema } from "graphql/utilities/schemaPrinter"
//import { stringify } from 'querystring';
//import { user } from 'firebase-functions/lib/providers/auth';

admin.initializeApp();

// // Start writing Firebase Functions
// // https://firebase.google.com/docs/functions/typescript
//

export const videoAPI = functions.https.onRequest(async (req, res) => {

    const key = req.body.key
    const tag = req.body.tag
    const regist = req.body.regist
    const userId = req.body.id

    const limitNum = 10

    var json:Object[] = []

    if (!key) {
        res.status(401).send("You need API-Key: key=... ")
        return
    }

    if (regist) {
        const randomId = admin.firestore().collection("Users").doc().id
        admin.firestore().collection("users").doc(userId).set({
            apiId: randomId
        })
        res.status(200).send(randomId)
        return
    } else {
        var user = await admin.firestore().collection('users').where('apiId', '==', key).get()
        var videosRef = await admin.firestore().collection('videos')
        if (user.size == 0) {
            res.status(401).send("API-Key is not correct ")
            return
        } else {
            if (tag) {
                var videosSnapShot = await videosRef.where('tag', 'array-contains', Number(tag)).limit(limitNum).get()
                videosSnapShot.forEach(video => {
                    json.push({
                        name:video.data().name,
                        tags:video.data().tag
                    })
                })
                res.setHeader('Content-Type', 'application/json')
                res.status(200).send(json)
                return
            } else {
                var videosSnapShot = await videosRef.limit(limitNum).get()
                videosSnapShot.forEach(video => {
                    json.push({
                        name:video.data().name,
                        tags:video.data().tag
                    })
                })
                res.setHeader('Content-Type', 'application/json')
                res.status(200).send(json)
                return
            }
        }        
    }
})
    
//     var userId = "VLw9XVGzTDMbaqTHumQ5"

//     var usersSnapShot =  await admin.firestore().collection("users").doc(userId).get()
    
//     const resolvers = {
//         Users: {
//             name() {
//                 return usersSnapShot.get("name")
//             },
//             favorTags() {
//                 return usersSnapShot.get("tags")
//             },
//         },
//     };

//     const schema = `
//     type Users {
//         name: String!
//         favorTags: [Tag]
//     }

//     type Tag {
//         score: Int!
//         tag: String!
//     }
//     `

//     makeExecutableSchema({ typeDefs: schema, resolvers })

//     const server = express().use(
//         bodyParser.json(),
//         graphqlExpress({ schema, context: {} })
//       )
      
//       exports.graphql = functions.https.onRequest(server)
// })


// export const helloWorld = functions.https.onRequest(async (request, response) => {

    // add videos 
    // for (var i = 0; i < 300; i++) {
    //     var randTagNum = Math.floor(Math.random() * 4) + 3
    //     var tags = []
    //     for (var j = 0; j < randTagNum; j++) {
    //         var randTag = Math.floor(Math.random() * 100)
    //         tags.push(randTag)
    //     }
    //     admin.firestore().collection('videos').add({
    //         name : `video${i}`,
    //         tag: tags,
    //     })
    // }
    // for (var i = 0; i < 300; i++) {
    //     var randTagNum = Math.floor(Math.random() * 4) + 3
    //     var tags = []
    //     for (var j = 0; j < randTagNum; j++) {
    //         var randTag = Math.floor(Math.random() * 100)
    //         tags.push(randTag)
    //     }
    //     admin.firestore().collection('videos').add({
    //         name : `video${i}`,
    //         tag: tags,
    //     })
    // }
    // for (var i = 0; i < 300; i++) {
    //     var randTagNum = Math.floor(Math.random() * 4) + 3
    //     var tags = []
    //     for (var j = 0; j < randTagNum; j++) {
    //         var randTag = Math.floor(Math.random() * 100)
    //         tags.push(randTag)
    //     }
    //     admin.firestore().collection('videos').add({
    //         name : `video${i}`,
    //         tag: tags,
    //     })
    // }



    // // add users
    // for (var i = 0; i < 1; i++) {
    //     admin.firestore().collection('users').add({
    //         name: `user${i}`,
    //     })
    //     console.log(`user${i}`)
    // }



    // // add history
    // var videos:FirebaseFirestore.QueryDocumentSnapshot[] = []
    // var videosSnapshot = await admin.firestore().collection('videos').get()
    // videosSnapshot.forEach(videoSnap => {
    //     videos.push(videoSnap)
    // })
    // await Promise.all(videos)

    // var users:FirebaseFirestore.QueryDocumentSnapshot[] = []
    // var usersSnapshot = await admin.firestore().collection('users').get()
    // usersSnapshot.forEach(userSnap => {
    //     users.push(userSnap)
    // })
    // await Promise.all(users)

    // for (var i = 0; i < 30; i++) {
    //     var videoNum = Math.floor(Math.random() * 901)
    //     var video = videos[videoNum].id
    //     var videoTag = videos[videoNum].data().tag
    //     admin.firestore().collection('history').add({
    //         video : `${video}`,
    //         user: `${users[0].id}`,
    //         tags: videoTag
    //     })
    // }


    // // search userId
    // var userName = 'user0'
    // var userIdSnapshot = await admin.firestore().collection('users').where("name", "==", userName).get()
    // var userId = userIdSnapshot.docs[0].id

    // var userId = "VLw9XVGzTDMbaqTHumQ5"

    // var tags:string[], tagList: String[] = []
    // var userHistorySnapshot = await admin.firestore().collection('history').where("user", "==", userId).get()

    
    // var histories: {[k: string]: any} = {}

    // userHistorySnapshot.forEach(userHistorySnap => {
    //     tags = userHistorySnap.data().tags
    //     for (var j = 0; j < tags.length; j++) {
    //         tagList.push(tags[j])
    //         histories[tags[j]] = histories[tags[j]] ? histories[tags[j]] + 1 : 1
    //     }
    // });


    // var objs:object[] = []
    // Object.keys(histories).forEach(function(key) {
    //     objs.push({
    //         tag: key,
    //         score: histories[key]
    //     })
    // })

    // function compare(a:{[k: string]: any}, b:{[k: string]: any}) {
    //     if (a.score < b.score)
    //       return 1;
    //     if (a.score > b.score)
    //       return -1;
    //     return 0;
    // }
      
    // objs.sort(compare);

    // admin.firestore().collection('users').doc(userId).update({
    //     favorTags: objs.slice(0,5)
    // })

    // console.log(objs.slice(0,5))
    
    // var user = await admin.firestore().collection('users').where("user", "==", userId).get()

    // var favorTags:object[]

    // user.forEach(userSnap => {
    //     favorTags = userSnap.data().favorTags
    // })
    // console.log()



    // response.send("Hello from Firebase!");
//});

